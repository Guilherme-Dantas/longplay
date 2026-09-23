import { useState } from "react";
import { Pressable, Text } from "react-native";
import Animated, { cubicBezier } from "react-native-reanimated";

import { colors } from "@/theme/colors";

export function ScaleButton({
  label,
  onPress,
  disabled = false,
  variant,
}: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  variant: "solid" | "glass";
}) {
  const [pressed, setPressed] = useState(false);
  const solid = variant === "solid";

  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      onPress={onPress}
      onPressIn={() => setPressed(true)}
      onPressOut={() => setPressed(false)}
      pressRetentionOffset={12}
      style={{ minHeight: 48 }}
    >
      <Animated.View
        style={{
          minHeight: 48,
          borderRadius: 999,
          alignItems: "center",
          justifyContent: "center",
          paddingHorizontal: 20,
          backgroundColor: solid ? (disabled ? "rgba(255,255,255,0.72)" : "#ffffff") : colors.glass,
          borderWidth: solid ? 0 : 1,
          borderColor: colors.line,
          transform: [{ scale: pressed && !disabled ? 0.97 : 1 }],
          transitionProperty: "transform",
          transitionDuration: 120,
          transitionTimingFunction: cubicBezier(0.23, 1, 0.32, 1),
        }}
      >
        <Text
          numberOfLines={1}
          style={{
            color: solid ? "#000000" : colors.text,
            fontFamily: "Geist_500Medium",
            fontSize: 15,
          }}
        >
          {label}
        </Text>
      </Animated.View>
    </Pressable>
  );
}
