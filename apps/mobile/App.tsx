import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Linking,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { useFonts, BodoniModa_600SemiBold } from "@expo-google-fonts/bodoni-moda";
import { Outfit_400Regular, Outfit_500Medium } from "@expo-google-fonts/outfit";

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

type AlbumPick = {
  album_id: string;
  name: string;
  artists: string[];
  duration_ms: number;
  duration_minutes: number;
  reason: string;
  spotify_url: string;
};

export default function App() {
  const [fontsLoaded] = useFonts({
    BodoniModa_600SemiBold,
    Outfit_400Regular,
    Outfit_500Medium,
  });
  const [minutes, setMinutes] = useState("45");
  const [criteria, setCriteria] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pick, setPick] = useState<AlbumPick | null>(null);

  async function pressPlay() {
    const duration = Number(minutes);
    const taste = criteria.trim();
    if (!Number.isFinite(duration) || duration <= 0 || duration > 240) {
      setError("Session length needs to be between 1 and 240 minutes.");
      return;
    }
    if (!taste) {
      setError("Say what you want to hear.");
      return;
    }
    setBusy(true);
    setError(null);
    setPick(null);
    try {
      const response = await fetch(`${API_URL}/runs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          duration_minutes: duration,
          criteria: taste,
          tolerance_minutes: 5,
        }),
      });
      const body = await response.json();
      if (!response.ok) {
        const detail = typeof body?.detail === "string" ? body.detail : "The picker did not answer.";
        throw new Error(detail);
      }
      setPick(body as AlbumPick);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The picker did not answer.");
    } finally {
      setBusy(false);
    }
  }

  if (!fontsLoaded) {
    return <View style={styles.screen} />;
  }

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <StatusBar style="light" />
      <Text style={styles.mark}>longplay</Text>
      <View style={styles.label}>
        <View style={styles.groove} />
        <TextInput
          value={minutes}
          onChangeText={setMinutes}
          keyboardType="number-pad"
          accessibilityLabel="Session length in minutes"
          style={styles.minutes}
        />
        <Text style={styles.unit}>minutes</Text>
        <View style={styles.stepper}>
          <Pressable onPress={() => nudge(minutes, -5, setMinutes)} style={styles.step}>
            <Text style={styles.stepText}>−5</Text>
          </Pressable>
          <Pressable onPress={() => nudge(minutes, 5, setMinutes)} style={styles.step}>
            <Text style={styles.stepText}>+5</Text>
          </Pressable>
        </View>
      </View>

      <TextInput
        value={criteria}
        onChangeText={setCriteria}
        placeholder="What you want to hear"
        placeholderTextColor="#8d867a"
        style={styles.criteria}
      />

      <Pressable
        onPress={pressPlay}
        disabled={busy}
        style={[styles.play, busy && styles.playBusy]}
      >
        {busy ? (
          <ActivityIndicator color="#f4e7c8" />
        ) : (
          <Text style={styles.playText}>Press play</Text>
        )}
      </Pressable>
      {busy ? <Text style={styles.hint}>Finding a record that fits the clock.</Text> : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}

      {pick ? (
        <View style={styles.result}>
          <Text style={styles.album}>{pick.name}</Text>
          <Text style={styles.artists}>{pick.artists.join(", ")}</Text>
          <Text style={styles.runtime}>{pick.duration_minutes} min on the record</Text>
          <Text style={styles.reason}>{pick.reason}</Text>
          <Pressable onPress={() => Linking.openURL(pick.spotify_url)}>
            <Text style={styles.link}>Open on Spotify</Text>
          </Pressable>
        </View>
      ) : null}
    </KeyboardAvoidingView>
  );
}

function nudge(current: string, delta: number, setMinutes: (value: string) => void) {
  const next = Math.min(240, Math.max(5, (Number(current) || 0) + delta));
  setMinutes(String(next));
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#14181f",
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 28,
    paddingVertical: 36,
  },
  mark: {
    fontFamily: "Outfit_500Medium",
    color: "#d9d3c7",
    letterSpacing: 6,
    textTransform: "uppercase",
    fontSize: 13,
    marginBottom: 28,
  },
  label: {
    width: 260,
    height: 260,
    borderRadius: 130,
    backgroundColor: "#f4e7c8",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 28,
  },
  groove: {
    position: "absolute",
    width: 228,
    height: 228,
    borderRadius: 114,
    borderWidth: 1,
    borderColor: "#c9b89a",
  },
  minutes: {
    fontFamily: "BodoniModa_600SemiBold",
    fontSize: 84,
    lineHeight: 92,
    color: "#1a140e",
    textAlign: "center",
    minWidth: 160,
    padding: 0,
  },
  unit: {
    fontFamily: "Outfit_400Regular",
    color: "#6d5840",
    letterSpacing: 2,
    textTransform: "uppercase",
    fontSize: 12,
    marginTop: -6,
  },
  stepper: {
    flexDirection: "row",
    gap: 12,
    marginTop: 10,
  },
  step: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  stepText: {
    fontFamily: "Outfit_500Medium",
    color: "#b85c38",
    fontSize: 14,
  },
  criteria: {
    width: "100%",
    maxWidth: 360,
    borderBottomWidth: 1,
    borderBottomColor: "#3a4038",
    color: "#f4e7c8",
    fontFamily: "Outfit_400Regular",
    fontSize: 18,
    paddingVertical: 10,
    marginBottom: 22,
  },
  play: {
    backgroundColor: "#b85c38",
    paddingVertical: 14,
    paddingHorizontal: 36,
    borderRadius: 999,
  },
  playBusy: {
    backgroundColor: "#6d3a28",
  },
  playText: {
    fontFamily: "Outfit_500Medium",
    color: "#f4e7c8",
    fontSize: 16,
    letterSpacing: 0.4,
  },
  hint: {
    marginTop: 14,
    fontFamily: "Outfit_400Regular",
    color: "#8d867a",
    fontSize: 14,
  },
  error: {
    marginTop: 14,
    fontFamily: "Outfit_400Regular",
    color: "#e7b2a0",
    fontSize: 14,
    textAlign: "center",
    maxWidth: 360,
  },
  result: {
    marginTop: 32,
    width: "100%",
    maxWidth: 360,
    alignItems: "center",
  },
  album: {
    fontFamily: "BodoniModa_600SemiBold",
    color: "#f4e7c8",
    fontSize: 32,
    textAlign: "center",
  },
  artists: {
    fontFamily: "Outfit_400Regular",
    color: "#d9d3c7",
    fontSize: 16,
    marginTop: 4,
  },
  runtime: {
    fontFamily: "Outfit_500Medium",
    color: "#b85c38",
    fontSize: 14,
    marginTop: 8,
    letterSpacing: 0.6,
  },
  reason: {
    fontFamily: "Outfit_400Regular",
    color: "#8d867a",
    fontSize: 14,
    textAlign: "center",
    marginTop: 10,
  },
  link: {
    fontFamily: "Outfit_500Medium",
    color: "#f4e7c8",
    marginTop: 16,
    textDecorationLine: "underline",
  },
});
