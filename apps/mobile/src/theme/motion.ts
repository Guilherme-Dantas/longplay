import { Easing } from "react-native-reanimated";

export const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);

export const SNAP_SPRING = { duration: 400, dampingRatio: 0.8 } as const;
