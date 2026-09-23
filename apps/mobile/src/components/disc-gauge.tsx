import { useEffect, useRef, useState } from "react";
import { Text, TextInput, View } from "react-native";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  cancelAnimation,
  Easing,
  useAnimatedReaction,
  useAnimatedStyle,
  useReducedMotion,
  useSharedValue,
  withRepeat,
  withTiming,
} from "react-native-reanimated";
import { scheduleOnRN } from "react-native-worklets";
import * as Haptics from "expo-haptics";
import Svg, { Circle } from "react-native-svg";

import { colors } from "@/theme/colors";
import { EASE_OUT } from "@/theme/motion";

const MIN = 5;
const MAX = 240;
const SIZE = 260;
const RADIUS = 96;
const CENTER = 110;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const PIXEL_RADIUS = (RADIUS / 220) * SIZE;

function snapTick() {
  if (process.env.EXPO_OS !== "ios") return;
  void Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
}

export function DiscGauge({
  mode,
  phrase,
  onMinutes,
}: {
  mode: "time" | "search" | "albums";
  phrase: string;
  onMinutes: (minutes: number) => void;
}) {
  const reduced = useReducedMotion();
  const minutesSv = useSharedValue(45);
  const searching = useSharedValue(0);
  const rotation = useSharedValue(0);
  const [label, setLabel] = useState("45");
  const editingRef = useRef(false);
  const onMinutesRef = useRef(onMinutes);
  onMinutesRef.current = onMinutes;

  useEffect(() => {
    searching.set(mode === "search" ? 1 : 0);
    if (mode === "search" && !reduced) {
      rotation.set(0);
      rotation.set(withRepeat(withTiming(360, { duration: 900, easing: Easing.linear }), -1, false));
      return;
    }
    cancelAnimation(rotation);
    rotation.set(0);
  }, [mode, reduced, rotation, searching]);

  function publish(next: number) {
    onMinutesRef.current(next);
    if (!editingRef.current) setLabel(String(next));
  }

  useAnimatedReaction(
    () => Math.round(minutesSv.get()),
    (next, prev) => {
      if (next !== prev) scheduleOnRN(publish, next);
    },
  );

  function seek(x: number, y: number) {
    "worklet";
    const angle = Math.atan2(y - SIZE / 2, x - SIZE / 2);
    let fromTop = angle + Math.PI / 2;
    if (fromTop < 0) fromTop += Math.PI * 2;
    const next = MIN + (fromTop / (Math.PI * 2)) * (MAX - MIN);
    minutesSv.set(Math.min(MAX, Math.max(MIN, next)));
  }

  const thumbStyle = useAnimatedStyle(() => {
    const ratio = (Math.min(MAX, Math.max(MIN, minutesSv.get())) - MIN) / (MAX - MIN);
    const angle = -Math.PI / 2 + ratio * Math.PI * 2;
    return {
      opacity: searching.get() === 1 ? 0 : 1,
      transform: [
        { translateX: SIZE / 2 + PIXEL_RADIUS * Math.cos(angle) - 7 },
        { translateY: SIZE / 2 + PIXEL_RADIUS * Math.sin(angle) - 7 },
      ],
    };
  });

  const sweepStyle = useAnimatedStyle(() => ({
    transform: [{ rotate: `${-90 + rotation.get()}deg` }],
  }));

  const faceStyle = useAnimatedStyle(() => ({
    opacity: searching.get() === 1 ? 0 : 1,
  }));

  const phraseStyle = useAnimatedStyle(() => ({
    opacity: searching.get() === 1 ? 1 : 0,
  }));

  const pan = Gesture.Pan()
    .enabled(mode === "time")
    .minDistance(0)
    .onBegin((event) => {
      seek(event.x, event.y);
    })
    .onUpdate((event) => {
      seek(event.x, event.y);
    })
    .onEnd(() => {
      const snapped = Math.round(Math.min(MAX, Math.max(MIN, minutesSv.get())));
      minutesSv.set(withTiming(snapped, { duration: 120, easing: EASE_OUT }));
      scheduleOnRN(snapTick);
    });

  function commitDraft() {
    const next = Math.min(MAX, Math.max(MIN, Math.round(Number(label)) || MIN));
    minutesSv.set(next);
    setLabel(String(next));
    onMinutes(next);
    editingRef.current = false;
  }

  return (
    <View style={{ width: SIZE, height: SIZE }}>
      <GestureDetector gesture={pan}>
        <View
          accessibilityRole="adjustable"
          accessibilityLabel="Session length"
          accessibilityValue={{ min: MIN, max: MAX, now: Number(label) || MIN }}
          accessibilityActions={[{ name: "increment" }, { name: "decrement" }]}
          onAccessibilityAction={(event) => {
            const current = Math.round(minutesSv.get());
            const next = event.nativeEvent.actionName === "increment" ? current + 5 : current - 5;
            const clamped = Math.min(MAX, Math.max(MIN, next));
            minutesSv.set(clamped);
            setLabel(String(clamped));
            onMinutes(clamped);
          }}
          style={{
            width: SIZE,
            height: SIZE,
            borderRadius: SIZE / 2,
            backgroundColor: "rgba(255,255,255,0.05)",
            borderWidth: 1,
            borderColor: colors.line,
            boxShadow: "inset 0 1px 0 rgba(255,255,255,0.35)",
          }}
        >
          <Svg width={SIZE} height={SIZE} viewBox="0 0 220 220">
            <Circle cx={CENTER} cy={CENTER} r={RADIUS} stroke="rgba(255,255,255,0.16)" strokeWidth={3} fill="none" />
          </Svg>
          {mode === "search" ? (
            <Animated.View style={[{ position: "absolute", top: 0, left: 0, width: SIZE, height: SIZE }, sweepStyle]}>
              <Svg width={SIZE} height={SIZE} viewBox="0 0 220 220">
                <Circle
                  cx={CENTER}
                  cy={CENTER}
                  r={RADIUS}
                  stroke="#ffffff"
                  strokeWidth={3}
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray="128 476"
                />
              </Svg>
            </Animated.View>
          ) : (
            <View
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: SIZE,
                height: SIZE,
                transform: [{ rotate: "-90deg" }],
              }}
            >
              <Svg width={SIZE} height={SIZE} viewBox="0 0 220 220">
                <Circle
                  cx={CENTER}
                  cy={CENTER}
                  r={RADIUS}
                  stroke="#ffffff"
                  strokeWidth={3}
                  fill="none"
                  strokeLinecap="round"
                  strokeDasharray={`${CIRCUMFERENCE} ${CIRCUMFERENCE}`}
                  strokeDashoffset={CIRCUMFERENCE * (1 - (Math.min(MAX, Math.max(MIN, Number(label) || MIN)) - MIN) / (MAX - MIN))}
                />
              </Svg>
            </View>
          )}
          <Animated.View
            style={[
              {
                position: "absolute",
                top: 0,
                left: 0,
                width: 14,
                height: 14,
                borderRadius: 7,
                backgroundColor: "#ffffff",
              },
              thumbStyle,
            ]}
          />
        </View>
      </GestureDetector>
      <View
        style={{
          position: "absolute",
          top: 42,
          right: 42,
          bottom: 42,
          left: 42,
          alignItems: "center",
          justifyContent: "center",
          pointerEvents: "box-none",
        }}
      >
        <Animated.View style={[{ alignItems: "center" }, faceStyle]}>
          <TextInput
            accessibilityLabel="Session length in minutes"
            editable={mode === "time"}
            value={label}
            onFocus={() => {
              editingRef.current = true;
            }}
            onChangeText={(text) => setLabel(text.replace(/\D/g, "").slice(0, 3))}
            onEndEditing={commitDraft}
            selectTextOnFocus
            inputMode="numeric"
            keyboardType="number-pad"
            style={{
              width: 150,
              padding: 0,
              color: "#ffffff",
              fontFamily: "Geist_600SemiBold",
              fontSize: 68,
              lineHeight: 72,
              fontVariant: ["tabular-nums"],
              textAlign: "center",
            }}
          />
          <Text style={{ marginTop: 4, color: colors.mute, fontFamily: "Geist_400Regular", fontSize: 13 }}>
            minutes
          </Text>
        </Animated.View>
        <Animated.Text
          accessibilityLiveRegion="polite"
          style={[
            {
              position: "absolute",
              left: 8,
              right: 8,
              textAlign: "center",
              color: "#ffffff",
              fontFamily: "Geist_500Medium",
              fontSize: 15,
              lineHeight: 20,
            },
            phraseStyle,
          ]}
        >
          {phrase}
        </Animated.Text>
      </View>
    </View>
  );
}
