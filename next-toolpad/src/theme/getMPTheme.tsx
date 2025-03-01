import type { } from '@mui/material/themeCssVarsAugmentation';
import { ThemeOptions, PaletteMode } from '@mui/material/styles';
import { getDesignTokens } from './themePrimitives';
import {
  inputsCustomizations,
  dataDisplayCustomizations,
  feedbackCustomizations,
  navigationCustomizations,
} from './customizations';
import theme from './theme';
export default function getMPTheme(mode: PaletteMode): ThemeOptions {

  return {
    ...getDesignTokens(mode),
    components: {
      ...inputsCustomizations,
      ...dataDisplayCustomizations,
      ...feedbackCustomizations,
      ...navigationCustomizations,
    },
    ...theme,
  };
}
