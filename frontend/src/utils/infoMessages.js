import { mainInfo } from './info/mainInfo'
import { reviewInfo } from './info/reviewInfo'
import { fileManagerInfo } from './info/fileManagerInfo'
import { settingsInfo } from './info/settingsInfo'
import { starterInfo } from './info/starterInfo'
import { visualizerInfo } from './info/visualizerInfo'

export const INFO_MESSAGES = {
  "default": "Info mode active: hover over any interface element to see its purpose and usage details.",
  ...mainInfo,
  ...reviewInfo,
  ...fileManagerInfo,
  ...settingsInfo,
  ...starterInfo,
  ...visualizerInfo
};