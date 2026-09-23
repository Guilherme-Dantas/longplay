import { useEffect, useState } from "react";
import { Pressable, View } from "react-native";
import { Image } from "expo-image";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, {
  ReduceMotion,
  type SharedValue,
  useAnimatedStyle,
  useSharedValue,
  withSpring,
} from "react-native-reanimated";
import { scheduleOnRN } from "react-native-worklets";

import type { AlbumFit } from "@/features/session/types";
import { toneFor } from "@/theme/colors";
import { SNAP_SPRING } from "@/theme/motion";

const SLEEVE = 208;
const GAP = 22;
const STRIDE = SLEEVE + GAP;

export function AlbumReel({
  albums,
  width,
  index,
  onIndex,
}: {
  albums: AlbumFit[];
  width: number;
  index: number;
  onIndex: (index: number) => void;
}) {
  const offset = useSharedValue(centerOffset(width, 0));
  const stage = useSharedValue(width);
  const indexSv = useSharedValue(0);

  useEffect(() => {
    stage.set(width);
    offset.set(centerOffset(width, indexSv.get()));
  }, [indexSv, offset, stage, width]);

  function focus(next: number, velocity = 0) {
    const clamped = Math.max(0, Math.min(albums.length - 1, next));
    indexSv.set(clamped);
    offset.set(
      withSpring(centerOffset(width, clamped), {
        ...SNAP_SPRING,
        velocity,
        reduceMotion: ReduceMotion.System,
      }),
    );
    onIndex(clamped);
  }

  const pan = Gesture.Pan()
    .enabled(albums.length > 1)
    .onUpdate((event) => {
      offset.set(centerOffset(stage.get(), indexSv.get()) + event.translationX);
    })
    .onEnd((event) => {
      const base = indexSv.get();
      let next = base - Math.round(event.translationX / STRIDE);
      if (Math.abs(event.velocityX) > 800) next = base + (event.velocityX < 0 ? 1 : -1);
      scheduleOnRN(focus, next, event.velocityX);
    });

  const trackStyle = useAnimatedStyle(() => ({
    transform: [{ translateX: offset.get() }],
  }));

  return (
    <GestureDetector gesture={pan}>
      <View style={{ flex: 1 }}>
        <Animated.View
          style={[
            {
              position: "absolute",
              left: 0,
              top: "50%",
              marginTop: -SLEEVE / 2,
              flexDirection: "row",
              gap: GAP,
              height: SLEEVE,
            },
            trackStyle,
          ]}
        >
          {albums.map((album, albumIndex) => (
            <Sleeve
              key={album.albumId}
              album={album}
              index={albumIndex}
              offset={offset}
              stage={stage}
              focused={albumIndex === index}
              onPress={() => focus(albumIndex)}
            />
          ))}
        </Animated.View>
      </View>
    </GestureDetector>
  );
}

function Sleeve({
  album,
  index,
  offset,
  stage,
  focused,
  onPress,
}: {
  album: AlbumFit;
  index: number;
  offset: SharedValue<number>;
  stage: SharedValue<number>;
  focused: boolean;
  onPress: () => void;
}) {
  const [coverFailed, setCoverFailed] = useState(false);
  const style = useAnimatedStyle(() => {
    const item = index * STRIDE + offset.get();
    const distance = Math.abs(item - (stage.get() - SLEEVE) / 2);
    const t = Math.min(1, distance / STRIDE);
    return {
      opacity: 1 - t * 0.58,
      transform: [{ scale: 1 - t * 0.16 }],
    };
  });
  const cover = coverFailed ? undefined : album.imageUrl;

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${album.name} by ${album.artists.join(", ")}`}
      onPress={onPress}
      style={{ width: SLEEVE, height: SLEEVE }}
    >
      <Animated.View
        style={[
          {
            width: SLEEVE,
            height: SLEEVE,
            borderRadius: SLEEVE / 2,
            backgroundColor: toneFor(album.albumId),
            alignItems: "center",
            justifyContent: "center",
            boxShadow: focused ? "0 0 0 2px #ffffff" : "inset 0 0 0 1px rgba(255,255,255,0.18)",
          },
          style,
        ]}
      >
        <View
          style={{
            width: SLEEVE,
            height: SLEEVE,
            borderRadius: SLEEVE / 2,
            overflow: "hidden",
          }}
        >
          {cover ? (
            <Image
              source={{ uri: cover }}
              recyclingKey={album.albumId}
              contentFit="cover"
              transition={180}
              accessible={false}
              onError={() => setCoverFailed(true)}
              style={{ width: SLEEVE, height: SLEEVE }}
            />
          ) : null}
        </View>
        <View
          style={{
            position: "absolute",
            top: SLEEVE / 2 - 9,
            left: SLEEVE / 2 - 9,
            width: 18,
            height: 18,
            borderRadius: 9,
            backgroundColor: "#070709",
            boxShadow: "0 0 0 8px rgba(0,0,0,0.25)",
            pointerEvents: "none",
          }}
        />
      </Animated.View>
    </Pressable>
  );
}

function centerOffset(width: number, index: number) {
  "worklet";
  return (width - SLEEVE) / 2 - index * STRIDE;
}
