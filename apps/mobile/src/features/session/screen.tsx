import { useEffect, useRef, useState } from "react";
import { Linking, ScrollView, Text, TextInput, View, type View as ViewType } from "react-native";
import Animated, { FadeOut } from "react-native-reanimated";

import { AlbumReel } from "@/components/album-reel";
import { DiscGauge } from "@/components/disc-gauge";
import { GlassCard, Wash } from "@/components/glass-card";
import { ScaleButton } from "@/components/scale-button";
import { SEARCH_LINES } from "@/features/session/lines";
import { PickError, requestShortlist } from "@/features/session/request-shortlist";
import { shortlistAlbums, type AlbumFit, type Shortlist } from "@/features/session/types";
import { colors } from "@/theme/colors";

type Mode = "time" | "search" | "albums";

export function SessionScreen() {
  const blurTarget = useRef<ViewType | null>(null);
  const request = useRef<AbortController | null>(null);
  const criteriaRef = useRef<TextInput>(null);
  const [minutes, setMinutes] = useState(45);
  const [criteria, setCriteria] = useState("");
  const [focused, setFocused] = useState(false);
  const [mode, setMode] = useState<Mode>("time");
  const [phrase, setPhrase] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [shortlist, setShortlist] = useState<Shortlist | null>(null);
  const [index, setIndex] = useState(0);
  const [stageWidth, setStageWidth] = useState(0);

  const albums = shortlist ? shortlistAlbums(shortlist) : [];
  const current = albums[index];
  const fieldOpen = focused || criteria.trim().length > 0;

  useEffect(() => () => request.current?.abort(), []);

  useEffect(() => {
    if (mode !== "search") return;
    let cursor = 0;
    setPhrase(SEARCH_LINES[0]);
    const timer = setInterval(() => {
      cursor = (cursor + 1) % SEARCH_LINES.length;
      setPhrase(SEARCH_LINES[cursor] ?? SEARCH_LINES[0]);
    }, 620);
    return () => clearInterval(timer);
  }, [mode]);

  async function pressPlay() {
    if (mode === "albums" && current) {
      if (current.spotifyUrl) await Linking.openURL(current.spotifyUrl);
      return;
    }
    if (mode !== "time") return;
    const taste = criteria.trim();
    if (!taste) {
      criteriaRef.current?.focus();
      return;
    }
    setError(null);
    setMode("search");
    const controller = new AbortController();
    request.current?.abort();
    request.current = controller;
    try {
      const next = await requestShortlist({ durationMinutes: minutes, criteria: taste }, controller.signal);
      if (controller.signal.aborted) return;
      setShortlist(next);
      setIndex(0);
      setMode("albums");
    } catch (caught) {
      if (controller.signal.aborted) return;
      setMode("time");
      setError(caught instanceof PickError ? caught.message : "The picker did not answer.");
    }
  }

  function restore() {
    request.current?.abort();
    setMode("time");
    setPhrase("");
    setError(null);
  }

  const showReel = mode === "albums" && albums.length > 0;

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <Wash targetRef={blurTarget} />
      <ScrollView
        contentInsetAdjustmentBehavior="automatic"
        keyboardShouldPersistTaps="handled"
        automaticallyAdjustKeyboardInsets
        contentContainerStyle={{
          flexGrow: 1,
          justifyContent: "center",
          paddingTop: 32,
          paddingBottom: 32,
          paddingHorizontal: 20,
          alignItems: "center",
        }}
      >
        <GlassCard blurTarget={blurTarget}>
          <Text style={{ color: colors.mute, fontFamily: "Geist_500Medium", fontSize: 13 }}>longplay</Text>
          <View
            onLayout={(event) => setStageWidth(event.nativeEvent.layout.width)}
            style={{ height: 276, marginTop: 8, marginHorizontal: -22, overflow: "hidden" }}
          >
            <Animated.View
              style={{
                position: "absolute",
                top: 0,
                right: 0,
                bottom: 0,
                left: 0,
                alignItems: "center",
                justifyContent: "center",
                opacity: showReel ? 0 : 1,
                transform: [{ scale: showReel ? 0.95 : 1 }],
                pointerEvents: showReel ? "none" : "auto",
                transitionProperty: ["opacity", "transform"],
                transitionDuration: 460,
              }}
            >
              <DiscGauge mode={mode} phrase={phrase} onMinutes={setMinutes} />
            </Animated.View>
            {showReel ? (
              <View style={{ position: "absolute", top: 0, right: 0, bottom: 0, left: 0 }}>
                <AlbumReel albums={albums} width={stageWidth} index={index} onIndex={setIndex} />
              </View>
            ) : null}
          </View>

          {showReel && current ? (
            <View style={{ marginTop: 6, alignItems: "center", gap: 6 }}>
              <Text
                style={{
                  color: colors.mute,
                  fontFamily: "Geist_500Medium",
                  fontSize: 12,
                  letterSpacing: 1.2,
                  textTransform: "uppercase",
                }}
              >
                {current.role === "recommendation" ? "Recommendation" : "Also fits"}
              </Text>
              <Text selectable style={{ color: colors.text, fontFamily: "Geist_500Medium", fontSize: 15 }}>
                {facts(current)}
              </Text>
              <Text
                selectable
                style={{
                  color: "#b7b7b7",
                  fontFamily: "Geist_400Regular",
                  fontSize: 13,
                  lineHeight: 18,
                  textAlign: "center",
                  maxWidth: 280,
                }}
              >
                {current.reason}
              </Text>
              {albums.length > 1 ? (
                <View style={{ flexDirection: "row", gap: 6, marginTop: 6 }}>
                  {albums.map((album, albumIndex) => (
                    <View
                      key={album.albumId}
                      style={{
                        width: 6,
                        height: 6,
                        borderRadius: 3,
                        backgroundColor: albumIndex === index ? "#ffffff" : "rgba(255,255,255,0.28)",
                      }}
                    />
                  ))}
                </View>
              ) : null}
            </View>
          ) : null}

          {mode !== "albums" ? (
            <Animated.View exiting={FadeOut.duration(180)} style={{ marginTop: 18 }}>
              <TextInput
                ref={criteriaRef}
                value={criteria}
                onChangeText={setCriteria}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                multiline
                placeholder="What you want to hear"
                placeholderTextColor="#666666"
                textAlignVertical="top"
                style={{
                  minHeight: fieldOpen ? 120 : 48,
                  borderRadius: 16,
                  borderCurve: "continuous",
                  borderWidth: 1,
                  borderColor: fieldOpen ? "rgba(255,255,255,0.18)" : "rgba(255,255,255,0.1)",
                  backgroundColor: fieldOpen ? colors.glassRaised : colors.field,
                  color: colors.text,
                  fontFamily: "Geist_400Regular",
                  fontSize: 16,
                  lineHeight: 24,
                  paddingHorizontal: 14,
                  paddingVertical: 12,
                }}
              />
            </Animated.View>
          ) : null}

          {error ? (
            <Text selectable style={{ marginTop: 12, color: "#ffb4ab", fontFamily: "Geist_400Regular", fontSize: 14 }}>
              {error}
            </Text>
          ) : null}

          {showReel ? (
            <View style={{ marginTop: 16 }}>
              <ScaleButton label="Look for something else" onPress={restore} variant="glass" />
            </View>
          ) : null}
          <View style={{ marginTop: showReel ? 12 : 16 }}>
            <ScaleButton
              label={mode === "search" ? "Looking" : showReel && current ? current.name : "Press play"}
              onPress={() => void pressPlay()}
              disabled={mode === "search"}
              variant="solid"
            />
          </View>
        </GlassCard>
      </ScrollView>
    </View>
  );
}

function facts(album: AlbumFit): string {
  const people = album.artists.join(", ");
  const minutes = `${Math.round(album.durationMinutes)} min`;
  if (album.year) return `${people} · ${album.year} · ${minutes}`;
  return `${people} · ${minutes}`;
}
