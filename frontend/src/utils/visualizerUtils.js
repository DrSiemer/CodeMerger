/**
 * Shared logic for the Project Visualizer treemap and JSON processing.
 */

export const getColorForDomain = (domain) => {
  const d = (domain || '').toLowerCase();
  if (d.includes('front')) return '#0D8319';
  if (d.includes('back') || d.includes('api') || d.includes('server')) return '#0078D4';
  if (d.includes('lib') || d.includes('util') || d.includes('core') || d.includes('shared')) return '#BB86FC';
  if (d.includes('infra') || d.includes('deploy') || d.includes('config') || d.includes('db')) return '#DE6808';
  return '#4B5563';
};

export const enrichNodes = (nodes, parentDomain = 'default', idTracker = { val: 0 }) => {
  let totalWeight = 0;
  nodes.forEach(node => {
    node.id = ++idTracker.val;
    node.domain = node.domain || parentDomain;
    node.color = getColorForDomain(node.domain);
    node.files = (node.files || []).map(f => typeof f === 'string' ? { path: f, description: '' } : f);
    node.weight = node.files.length || 1;

    if (node.children && node.children.length > 0) {
      node.weight += enrichNodes(node.children, node.domain, idTracker);
    }
    totalWeight += node.weight;
  });
  return totalWeight;
};

export const computeLayouts = (node) => {
  if (!node.children || node.children.length === 0) return;
  const sortedChildren = [...node.children].sort((a, b) => b.weight - a.weight);

  let cx = 0, cy = 0, cw = 100, ch = 100;
  let total = sortedChildren.reduce((s, c) => s + c.weight, 0);

  sortedChildren.forEach((child, index) => {
    let ratio = child.weight / total;
    if (index === sortedChildren.length - 1) {
      child.layout = { x: cx, y: cy, w: cw, h: ch };
    } else {
      if (cw > ch) {
        let splitW = cw * ratio;
        child.layout = { x: cx, y: cy, w: splitW, h: ch };
        cx += splitW;
        cw -= splitW;
      } else {
        let splitH = ch * ratio;
        child.layout = { x: cx, y: cy, w: cw, h: splitH };
        cy += splitH;
        ch -= splitH;
      }
    }
    total -= child.weight;
    if (child.children && child.children.length > 0) {
       computeLayouts(child);
    }
  });
};

export const getAllFilesUnderNode = (node) => {
  let paths = [...(node.files || [])].map(f => f.path);
  if (node.children) {
    node.children.forEach((child) => {
      paths = [...paths, ...getAllFilesUnderNode(child)];
    });
  }
  return paths;
};

export const extractJSON = (raw) => {
  const startIdx = raw.indexOf("[") !== -1 ? Math.min(raw.indexOf("["), raw.indexOf("{")) : raw.indexOf("{");
  const endIdx = raw.lastIndexOf("]") !== -1 ? Math.max(raw.lastIndexOf("]"), raw.lastIndexOf("}")) : raw.lastIndexOf("}");
  if (startIdx === -1 || endIdx === -1) throw new Error("JSON structure not found.");
  const jsonStr = raw.substring(startIdx, endIdx + 1);
  try {
    return JSON.parse(jsonStr);
  } catch (e) {
    throw new Error("Invalid JSON syntax: " + e.message);
  }
};

export const nodeHasMatch = (node, query) => {
  if (!query) return true;
  const q = query.toLowerCase();

  if (node.files && node.files.some(f =>
    f.path.toLowerCase().includes(q) ||
    (f.description && f.description.toLowerCase().includes(q))
  )) {
    return true;
  }

  if (node.children) {
    return node.children.some(child => nodeHasMatch(child, query));
  }

  return false;
};

export const findAndAddFileToNode = (root, fileName, parentName, description) => {
  // If this node is the target parent, add the file
  if (root.name.toLowerCase() === parentName.toLowerCase()) {
    if (!root.files) root.files = [];
    // Prevent duplicates
    if (!root.files.some(f => f.path === fileName)) {
      root.files.push({ path: fileName, description: description });
    }
    return true;
  }

  // Recursive search in children
  if (root.children) {
    for (let child of root.children) {
      if (findAndAddFileToNode(child, fileName, parentName, description)) return true;
    }
  }

  return false;
};

export const removeFileFromTree = (root, filePath) => {
  if (root.files) {
    const initialLen = root.files.length;
    root.files = root.files.filter(f => f.path !== filePath);
    if (root.files.length < initialLen) return true;
  }

  if (root.children) {
    for (let child of root.children) {
      if (removeFileFromTree(child, filePath)) return true;
    }
  }

  return false;
};