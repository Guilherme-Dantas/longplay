import { useEffect, useState, type ReactNode, type RefObject } from "react";
import { AccessibilityInfo, View, type View as ViewType } from "react-native";
import { BlurTargetView, BlurView } from "expo-blur";
import { GlassView, isGlassEffectAPIAvailable, isLiquidGlassAvailable } from "expo-glass-effect";
import Svg, { Defs, RadialGradient, Rect, Stop } from "react-native-svg";

import { colors } from "@/theme/colors";

const frame = {
  width: "100%" as const,
  maxWidth: 420,
  borderRadius: 28,
  borderCurve: "continuous" as const,
  paddingTop: 28,
  paddingBottom: 22,
  paddingHorizontal: 22,
};

export function Wash({ targetRef }: { targetRef: RefObject<ViewType | null> }) {
  return (
    <BlurTargetView ref={targetRef} style={{ position: "absolute", top: 0, right: 0, bottom: 0, left: 0 }}>
      <Svg width="100%" height="100%">
        <Defs>
          <RadialGradient id="wash-blue" cx="18%" cy="12%" r="42%">
            <Stop offset="0%" stopColor={colors.washBlue} stopOpacity={1} />
            <Stop offset="70%" stopColor={colors.washBlue} stopOpacity={0} />
          </RadialGradient>
          <RadialGradient id="wash-white" cx="86%" cy="78%" r="36%">
            <Stop offset="0%" stopColor={colors.washWhite} stopOpacity={1} />
            <Stop offset="68%" stopColor={colors.washWhite} stopOpacity={0} />
          </RadialGradient>
        </Defs>
        <Rect width="100%" height="100%" fill="url(#wash-blue)" />
        <Rect width="100%" height="100%" fill="url(#wash-white)" />
      </Svg>
    </BlurTargetView>
  );
}

export function GlassCard({
  children,
  blurTarget,
}: {
  children: ReactNode;
  blurTarget: RefObject<ViewType | null>;
}) {
  const [solid, setSolid] = useState(false);

  useEffect(() => {
    let alive = true;
    const read = AccessibilityInfo.isReduceTransparencyEnabled;
    if (typeof read === "function") {
      void read().then((enabled) => {
        if (alive) setSolid(enabled);
      });
    }
    const subscription = AccessibilityInfo.addEventListener?.("reduceTransparencyChanged", setSolid);
    return () => {
      alive = false;
      subscription?.remove();
    };
  }, []);

  if (!solid && isLiquidGlassAvailable() && isGlassEffectAPIAvailable()) {
    return (
      <GlassView colorScheme="dark" style={frame}>
        {children}
      </GlassView>
    );
  }

  if (solid) {
    return <View style={[frame, { backgroundColor: colors.solid }]}>{children}</View>;
  }

  return (
    <BlurView
      intensity={80}
      tint="systemChromeMaterialDark"
      blurTarget={blurTarget}
      blurMethod={process.env.EXPO_OS === "android" ? "dimezisBlurViewSdk31Plus" : undefined}
      style={[
        frame,
        {
          overflow: "hidden",
          backgroundColor: colors.glass,
          borderWidth: 1,
          borderColor: colors.line,
          boxShadow: colors.cardShadow,
        },
      ]}
    >
      {children}
    </BlurView>
  );
}
