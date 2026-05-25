const DRAFT_KEY = 'standardization_draft'
const SAVE_DELAY = 3000

let saveTimer = null
let saveCallback = null

export function initDraftManager(onStatusChange) {
  saveCallback = onStatusChange
}

export function getDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (!raw) return null
    const draft = JSON.parse(raw)
    if (!draft || !draft.savedAt) return null
    return draft
  } catch (e) {
    return null
  }
}

export function hasDraft() {
  return getDraft() !== null
}

export function saveDraft(data) {
  try {
    const draft = {
      ...data,
      savedAt: new Date().toISOString()
    }
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft))
    return true
  } catch (e) {
    return false
  }
}

export function scheduleAutoSave(getData) {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }

  if (saveCallback) {
    saveCallback('unsaved')
  }

  saveTimer = setTimeout(() => {
    const success = saveDraft(getData())
    if (saveCallback) {
      saveCallback(success ? 'saved' : 'error')
    }
    saveTimer = null
  }, SAVE_DELAY)
}

export function saveNow(getData) {
  if (saveTimer) {
    clearTimeout(saveTimer)
    saveTimer = null
  }

  const success = saveDraft(getData())
  if (saveCallback) {
    saveCallback(success ? 'saved' : 'error')
  }
  return success
}

export function clearDraft() {
  try {
    localStorage.removeItem(DRAFT_KEY)
    if (saveCallback) {
      saveCallback('idle')
    }
    return true
  } catch (e) {
    return false
  }
}

export function formatSaveTime(isoString) {
  if (!isoString) return ''
  const d = new Date(isoString)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}