import { ref, computed, watch, onMounted } from "vue";
import { useAppState } from "./useAppState";
import {
  computeLayouts,
  getAllFilesUnderNode,
  extractJSON,
  getColorForDomain,
  moveRootFilesToMisc,
  findAndAddFileToNode,
  removeFileFromTree
} from "../utils/visualizerUtils";

export function useVisualizer() {
  const {
    activeProject,
    getVisualizerPrompt,
    getVisualizerUpdatePrompt,
    getVisualizerAmendPrompt,
    getVisualizerErrorPrompt,
    copyVisualizerNodeCode,
    saveVisualizerMap,
    statusMessage,
    getFileContent,
    copyText
  } = useAppState();

  const viewState = ref("init"); // 'init' | 'visualizing' | 'updating'
  const navPath = ref([]);
  const hoveredNode = ref(null);
  const targetScrollPath = ref(null);
  const highlightedLines = ref([]);
  const isCodeLoading = ref(false);
  const parseError = ref("");
  const draftTree = ref(null);
  const missingPathsList = ref([]);
  const unknownPathsList = ref([]);
  const duplicateEntriesList = ref([]);

  const currentNavNode = computed(() => navPath.value[navPath.value.length - 1] || null);

  const displayNode = computed(() => hoveredNode.value || currentNavNode.value);

  const rankedMtimeMap = computed(() => {
    const files = [...activeProject.selectedFiles]
      .filter(f => f.mtime)
      .sort((a, b) => {
        if (b.mtime !== a.mtime) return b.mtime - a.mtime;
        return a.path.localeCompare(b.path);
      });

    const map = {};
    const count = files.length;
    if (count === 1) map[files[0].path] = 0;
    else if (count > 1) {
      files.forEach((f, idx) => { map[f.path] = idx / (count - 1); });
    }
    return map;
  });

  const mapSyncState = computed(() => {
    if (!activeProject.visualizerMap || !activeProject.visualizerMap.file_hashes) return 'SYNCED';
    const mapHashes = activeProject.visualizerMap.file_hashes;
    const currentFiles = activeProject.selectedFiles || [];
    const mapPaths = Object.keys(mapHashes);
    const currentPaths = currentFiles.map(f => f.path);

    if (mapPaths.length !== currentPaths.length || mapPaths.some(p => !currentPaths.includes(p)) || currentPaths.some(p => !mapPaths.includes(p))) {
      return 'PATHS_CHANGED';
    }
    if (currentFiles.some(f => (f.hash || null) !== (mapHashes[f.path] || null))) {
      return 'CONTENT_CHANGED';
    }
    return 'SYNCED';
  });

  const syncMessage = computed(() => {
    if (mapSyncState.value === 'PATHS_CHANGED') return 'Map is out of sync (files were added or removed).';
    if (mapSyncState.value === 'CONTENT_CHANGED') return 'Map is somewhat out of sync (files were modified).';
    return '';
  });

  const canCopy = computed(() => {
    const node = currentNavNode.value;
    if (!node || node.isFile) return false;
    return navPath.value.length > 1 && !hoveredNode.value;
  });

  const loadTree = (root) => {
    const idTracker = { val: 0 };
    moveRootFilesToMisc(root);
    const reEnrich = (node, parentDomain = 'default') => {
      node.id = ++idTracker.val;
      node.domain = node.domain || parentDomain;
      node.color = getColorForDomain(node.domain);
      if (!node.files) node.files = [];
      node.files = node.files.map(f => typeof f === 'string' ? { path: f, description: '' } : f);
      node.weight = node.files.length || 1;
      if (node.children?.length) {
        node.weight += node.children.reduce((acc, c) => acc + reEnrich(c, node.domain), 0);
      }
      return node.weight;
    };
    reEnrich(root);
    computeLayouts(root);
    navPath.value = [root];
  };

  const processRawResponse = async (raw) => {
    parseError.value = "";
    try {
      const data = extractJSON(raw);
      let root;
      if (data.amendments) {
        const sourceTree = draftTree.value || activeProject.visualizerMap?.tree;
        if (!sourceTree) throw new Error("No existing tree to amend.");
        root = JSON.parse(JSON.stringify(sourceTree));

        if (Array.isArray(data.amendments.remove)) {
          data.amendments.remove.forEach(path => removeFileFromTree(root, path));
        }

        const addList = Array.isArray(data.amendments.add) ? data.amendments.add : (Array.isArray(data.amendments) ? data.amendments : []);
        addList.forEach(item => {
          const added = findAndAddFileToNode(root, item.path, item.parent, item.description);
          if (!added) {
            if (!root.children) root.children = [];
            let newNode = root.children.find(c => c.name.toLowerCase() === item.parent.toLowerCase());
            if (!newNode) {
              newNode = { name: item.parent, description: 'Newly categorized artifacts.', domain: 'default', children: [], files: [] };
              root.children.push(newNode);
            }
            newNode.files.push({ path: item.path, description: item.description });
          }
        });
      } else {
        root = Array.isArray(data) ? (data.length === 1 ? data[0] : { name: 'System Architecture', description: 'Complete project structure', domain: 'default', children: data, files: [] }) : data;
      }

      moveRootFilesToMisc(root);
      const idTracker = { val: 0 };
      const reEnrich = (node, parentDomain = 'default') => {
        node.id = ++idTracker.val;
        node.domain = node.domain || parentDomain;
        node.color = getColorForDomain(node.domain);
        if (!node.files) node.files = [];
        node.files = node.files.map(f => typeof f === 'string' ? { path: f, description: '' } : f);
        node.weight = node.files.length || 1;
        if (node.children?.length) {
          node.weight += node.children.reduce((acc, c) => acc + reEnrich(c, node.domain), 0);
        }
        return node.weight;
      };
      reEnrich(root);

      const parsedPaths = getAllFilesUnderNode(root);
      const currentPaths = activeProject.selectedFiles.map(f => f.path);
      const missing = currentPaths.filter(p => !parsedPaths.includes(p));
      const unknown = parsedPaths.filter(p => !currentPaths.includes(p));
      const dupes = parsedPaths.filter((item, index) => parsedPaths.indexOf(item) !== index);

      // Silently remove hallucinated files from the tree to avoid error-blocking or broken UI nodes
      if (unknown.length > 0) {
        unknown.forEach(p => removeFileFromTree(root, p));
      }

      // We always store the result in the draftTree so following amendments are additive
      draftTree.value = root;
      missingPathsList.value = missing;
      unknownPathsList.value = []; // Cleared as they are now ignored/removed
      duplicateEntriesList.value = [...new Set(dupes)];

      if (missing.length || dupes.length) {
        let errs = [];
        if (missing.length) errs.push(`Missing Files:\n${JSON.stringify(missing.sort(), null, 2)}`);
        if (dupes.length) errs.push(`Duplicate Entries Found:\n${JSON.stringify(duplicateEntriesList.value.sort(), null, 2)}`);
        throw new Error(errs.join('\n\n'));
      }

      computeLayouts(root);
      draftTree.value = null;
      const file_hashes = {};
      activeProject.selectedFiles.forEach(f => { file_hashes[f.path] = f.hash || null; });
      await saveVisualizerMap({ tree: root, file_hashes });
      loadTree(root);
      viewState.value = "visualizing";
    } catch (err) {
      parseError.value = err.message;
    }
  };

  const handleCopyPrompt = async () => {
    if (viewState.value === 'updating' && activeProject.visualizerMap) {
      const mapHashes = activeProject.visualizerMap.file_hashes || {};
      const mapPaths = Object.keys(mapHashes);
      const currentPaths = activeProject.selectedFiles.map(f => f.path);
      const missingPaths = currentPaths.filter(p => !mapPaths.includes(p));
      const obsoletePaths = mapPaths.filter(p => !currentPaths.includes(p));
      const prevJson = JSON.stringify(activeProject.visualizerMap.tree, (k, v) => ['id', 'layout', 'color', 'weight'].includes(k) ? undefined : v, 2);
      const prompt = await getVisualizerUpdatePrompt(prevJson, missingPaths, obsoletePaths);
      if (prompt) await copyText(prompt);
    } else {
      const prompt = await getVisualizerPrompt();
      if (prompt) await copyText(prompt);
    }
  };

  const handleCopyAmendPrompt = async () => {
    const prompt = await getVisualizerAmendPrompt(missingPathsList.value, duplicateEntriesList.value);
    if (prompt) {
      await copyText(prompt);
      statusMessage.value = "Copied amend prompt.";
    }
  };

  const copyCorrectionPrompt = async () => {
    const prompt = await getVisualizerErrorPrompt(parseError.value);
    if (prompt) {
      await copyText(prompt);
      statusMessage.value = "Copied correction prompt.";
      // Reset error state to hide the error block and return to Step 1
      parseError.value = "";
    }
  };

  const handleCopyNodeCode = async (node) => {
    const paths = getAllFilesUnderNode(node);
    if (paths.length) statusMessage.value = await copyVisualizerNodeCode(paths);
  };

  const nukeVisualizerMap = async () => {
    if (confirm("Reset the map? This cannot be undone.")) {
      const success = await saveVisualizerMap(null);
      if (success) { viewState.value = "init"; navPath.value = []; activeProject.visualizerMap = null; }
    }
  };

  const diveIntoFile = (f) => {
    navPath.value.push({
      id: 'file-' + f.path,
      isFile: true,
      name: f.path.split('/').pop(),
      path: f.path,
      description: f.description,
      domain: currentNavNode.value?.domain,
      color: currentNavNode.value?.color
    });
  };

  const scrollToAndHighlight = (path) => {
    targetScrollPath.value = path;
    // Reset after a short delay so the same path can be clicked again to re-trigger the highlight
    setTimeout(() => {
      if (targetScrollPath.value === path) targetScrollPath.value = null;
    }, 2000);
  };

  watch(currentNavNode, async (node) => {
    if (node?.isFile) {
      isCodeLoading.value = true;
      highlightedLines.value = [];
      const content = await getFileContent(node.path);
      if (content !== null && window.pywebview) highlightedLines.value = await window.pywebview.api.get_syntax_highlight(content, node.path);
      isCodeLoading.value = false;
    } else highlightedLines.value = [];
  });

  watch(navPath, () => { if (hoveredNode.value) hoveredNode.value = null; }, { deep: true });

  onMounted(async () => {
    if (window.pywebview && !document.getElementById('pygments-css')) {
      const css = await window.pywebview.api.get_pygments_style();
      const style = document.createElement('style');
      style.id = 'pygments-css'; style.innerHTML = css; document.head.appendChild(style);
    }
    if (activeProject.visualizerMap?.tree) { loadTree(activeProject.visualizerMap.tree); viewState.value = "visualizing"; }
  });

  return {
    viewState, navPath, hoveredNode, targetScrollPath, parseError, currentNavNode, displayNode,
    rankedMtimeMap, canCopy, mapSyncState, syncMessage,
    highlightedLines, isCodeLoading,
    loadTree, processRawResponse, handleCopyPrompt,
    handleCopyAmendPrompt, copyCorrectionPrompt,
    handleCopyNodeCode, nukeVisualizerMap, diveIntoFile, scrollToAndHighlight
  };
}