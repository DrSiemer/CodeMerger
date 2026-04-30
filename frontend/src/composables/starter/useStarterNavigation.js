import { ref, computed } from 'vue'

export function useStarterNavigation(pData) {
  const currentStep = ref(1)
  const maxAccessibleStep = ref(1)

  const stepNames = {
    1: 'Details',
    2: 'Base Files',
    3: 'Concept',
    4: 'Stack',
    5: 'System Design',
    6: 'TODO',
    7: 'Generate'
  }

  const activeStepsList = computed(() => {
    const steps = [1]
    if (pData.starting_mode === 'base') steps.push(2)
    steps.push(3, 4, 5, 6, 7)
    return steps
  })

  const isLookingBack = computed(() => currentStep.value < maxAccessibleStep.value)

  const recalcProgress = () => {
    const hasDetails = !!pData.starting_mode
    const hasConcept = !!pData.concept_md
    const hasStack = pData.stack && pData.stack.length > 0
    const hasDesign = !!pData.design_md
    const hasTodo = !!pData.todo_md

    let targetMax = 1
    if (hasDetails) {
      targetMax = pData.starting_mode === 'base' ? 2 : 3
      if (hasConcept) {
        targetMax = 4
        if (hasStack) {
          targetMax = 5
          if (hasDesign) {
            targetMax = 6
            if (hasTodo) targetMax = 7
          }
        }
      }
    }
    if (targetMax > maxAccessibleStep.value) {
      maxAccessibleStep.value = targetMax
    }
  }

  const isNextDisabled = computed(() => {
    if (currentStep.value === 1) return !pData.starting_mode
    const hasDiffs = (baselines) => baselines && Object.values(baselines).some(v => v !== undefined)

    if (currentStep.value === 3) return hasDiffs(pData.concept_baselines) || !pData.concept_md.trim()
    if (currentStep.value === 5) return hasDiffs(pData.design_baselines) || !pData.design_md.trim()
    if (currentStep.value === 6) return hasDiffs(pData.todo_baselines) || !pData.todo_md.trim()
    return false
  })

  const goToStep = (step) => {
    if (step <= maxAccessibleStep.value || step === 2) {
      if (step === 3 && !pData.goal.trim() && pData.name.trim()) {
        pData.goal = pData.name
      }
      currentStep.value = step
    }
  }

  const prevStep = () => {
    const idx = activeStepsList.value.indexOf(currentStep.value)
    if (idx > 0) goToStep(activeStepsList.value[idx - 1])
  }

  const nextStep = () => {
    const idx = activeStepsList.value.indexOf(currentStep.value)
    if (idx < activeStepsList.value.length - 1) {
      const targetStep = activeStepsList.value[idx + 1]

      const validationChecks = {
        3: { content: pData.concept_md, segments: pData.concept_segments, label: "concept document" },
        5: { content: pData.design_md, segments: pData.design_segments, label: "system design" },
        6: { content: pData.todo_md, segments: pData.todo_segments, label: "TODO plan" }
      }

      const check = validationChecks[currentStep.value]
      if (check && !check.content) {
        if (Object.keys(check.segments).length > 0) {
          alert(`You must merge the ${check.label} segments into a final document before proceeding.`)
        } else {
          alert(`The ${check.label} cannot be empty.`)
        }
        return
      }

      if (targetStep > maxAccessibleStep.value) maxAccessibleStep.value = targetStep
      goToStep(targetStep)
    }
  }

  return {
    currentStep,
    maxAccessibleStep,
    stepNames,
    activeStepsList,
    isLookingBack,
    isNextDisabled,
    recalcProgress,
    goToStep,
    prevStep,
    nextStep
  }
}