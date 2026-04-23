export function useStarter() {
  const clearStarterSession = async () => {
    if (window.pywebview) {
      return await window.pywebview.api.clear_starter_session()
    }
    return true
  }

  const getStarterSession = async () => window.pywebview ? await window.pywebview.api.get_starter_session() : {}
  const saveStarterSession = async (data) => window.pywebview ? await window.pywebview.api.save_starter_session(data) : true
  const exportStarterConfig = async (data) => window.pywebview ? await window.pywebview.api.export_starter_config(data) : false
  const loadStarterConfig = async () => window.pywebview ? await window.pywebview.api.load_starter_config() : null
  const getConceptQuestions = async () => window.pywebview ? await window.pywebview.api.get_concept_questions() : {}
  const getDesignQuestions = async () => window.pywebview ? await window.pywebview.api.get_design_questions() : {}
  const getTodoQuestions = async () => window.pywebview ? await window.pywebview.api.get_todo_questions() : {}
  const getTodoTemplate = async () => window.pywebview ? await window.pywebview.api.get_todo_template() : ""
  const getBaseProjectData = async (path) => window.pywebview ? await window.pywebview.api.get_base_project_data(path) : null
  const getBaseFileTree = async (path, filter, ext, git, sel) => window.pywebview ? await window.pywebview.api.get_base_file_tree(path, filter, ext, git, sel) : []
  const getTokenCountForPath = async (base, rel) => window.pywebview ? await window.pywebview.api.get_token_count_for_path(base, rel) : 0
  const generateConceptPrompt = async (data, qMap) => window.pywebview ? await window.pywebview.api.generate_concept_prompt(data, qMap) : ""
  const generateStackPrompt = async (data) => window.pywebview ? await window.pywebview.api.generate_stack_prompt(data) : ""
  const generateDesignPrompt = async (data, qMap) => window.pywebview ? await window.pywebview.api.generate_design_prompt(data, qMap) : ""
  const generateTodoPrompt = async (data, qMap) => window.pywebview ? await window.pywebview.api.generate_todo_prompt(data, qMap) : ""
  const generateNameSuggestionsPrompt = async (data) => window.pywebview ? await window.pywebview.api.generate_name_suggestions_prompt(data) : ""
  const generateMasterPrompt = async (data) => window.pywebview ? await window.pywebview.api.generate_master_prompt(data) : ""
  const parseStarterSegments = async (text) => window.pywebview ? await window.pywebview.api.parse_starter_segments(text) : {}
  const assembleStarterDocument = async (segments, order, names) => window.pywebview ? await window.pywebview.api.assemble_starter_document(segments, order, names) : ""
  const getStarterRewritePrompt = async (inst, targets, Hacker, names, data, merged) => window.pywebview ? await window.pywebview.api.get_starter_rewrite_prompt(inst, targets, Hacker, names, data, merged) : ""
  const getStarterSyncPrompt = async (k, names, data, targets, Hacker) => window.pywebview ? await window.pywebview.api.get_starter_sync_prompt(k, names, data, targets, Hacker) : ""
  const getStarterQuestionPrompt = async (ctx, name, text, q) => window.pywebview ? await window.pywebview.api.get_starter_question_prompt(ctx, name, text, q) : ""
  const getStarterPivotPrompt = async (alt, text, k, targets, refs, names, data, merged) => window.pywebview ? await window.pywebview.api.get_starter_pivot_prompt(alt, text, k, targets, refs, names, data, merged) : ""
  const mapParsedSegmentsToKeys = async (parsed, names) => window.pywebview ? await window.pywebview.api.map_parsed_segments_to_keys(parsed, names) : {}
  const createStarterProject = async (output, includeRef, pitch, data) => window.pywebview ? await window.pywebview.api.create_starter_project(output, includeRef, pitch, data) : null
  const createStarterProjectOverwrite = async (output, includeRef, pitch, data) => window.pywebview ? await window.pywebview.api.create_starter_project_overwrite(output, includeRef, pitch, data) : null
  const selectDirectory = async () => window.pywebview ? await window.pywebview.api.select_directory() : null
  const openPath = async (path) => window.pywebview ? await window.pywebview.api.open_path(path) : false
  const getRandomSillySuggestion = async () => window.pywebview ? await window.pywebview.api.get_random_silly_suggestion() : "e.g. My Next Big Idea"

  return {
    clearStarterSession,
    getStarterSession,
    saveStarterSession,
    exportStarterConfig,
    loadStarterConfig,
    getConceptQuestions,
    getDesignQuestions,
    getTodoQuestions,
    getTodoTemplate,
    getBaseProjectData,
    getBaseFileTree,
    getTokenCountForPath,
    generateConceptPrompt,
    generateStackPrompt,
    generateDesignPrompt,
    generateTodoPrompt,
    generateNameSuggestionsPrompt,
    generateMasterPrompt,
    parseStarterSegments,
    assembleStarterDocument,
    getStarterRewritePrompt,
    getStarterSyncPrompt,
    getStarterQuestionPrompt,
    getStarterPivotPrompt,
    mapParsedSegmentsToKeys,
    createStarterProject,
    createStarterProjectOverwrite,
    selectDirectory,
    openPath,
    getRandomSillySuggestion
  }
}