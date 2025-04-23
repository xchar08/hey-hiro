"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import {
  ChakraProvider,
  Box,
  Flex,
  IconButton,
  Button,
} from "@chakra-ui/react";
import { FaMicrophone, FaStop, FaCog } from "react-icons/fa";
import TutorialTooltip from "./components/TutorialTooltip";
import SettingsModal from "./components/SettingsModal";

const COMPANION = process.env.NEXT_PUBLIC_COMPANION_API_URL!;

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [showRun, setShowRun] = useState(false);
  const [isSettingsOpen, setSettingsOpen] = useState(false);
  const [auraColor, setAuraColor] = useState("#00ff00");
  const [voiceSpeed, setVoiceSpeed] = useState(1.2);
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [cerebrasKey, setCerebrasKey] = useState("");
  const recogRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem("cerebrasKey");
    if (saved) setCerebrasKey(saved);

    if ("SpeechRecognition" in window || "webkitSpeechRecognition" in window) {
      const Ctor =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;
      const rec: SpeechRecognition = new Ctor();
      rec.continuous = true;
      rec.interimResults = true;
      rec.lang = "en-US";

      rec.onstart = () => {};
      rec.onend = () => {};

      rec.onresult = (e) => {
        let txt = "";
        for (let i = e.resultIndex; i < e.results.length; i++) {
          txt += e.results[i][0].transcript;
        }
        setTranscript(txt);
        if (
          e.results[e.results.length - 1].isFinal &&
          txt.trim().toLowerCase().startsWith("hey hero")
        ) {
          processVoiceCommand(txt.trim().slice(8).trim());
        }
      };

      recogRef.current = rec;
    } else {
      setResponse("Speech Recognition not supported.");
    }
  }, []);

  const startListening = () => recogRef.current?.start();
  const stopListening = () => recogRef.current?.stop();

  const invokeComp = (ep: string, body: any) =>
    axios.post(`${COMPANION}/${ep}`, body);

  const processVoiceCommand = useCallback(async (cmd: string) => {
    setResponse("");
    let m: RegExpMatchArray | null;

    // Hover
    if (
      (m = cmd.match(
        /make drones? ([\d,\s]+) hover(?: for (\d+) seconds)?(?: at height ([\d.]+) meter)?/
      ))
    ) {
      const args = [
        "--config",
        "scripted_flight/config/drones.json",
        "--demo",
        "hover",
      ];
      if (m[2]) args.push("--hover_duration", m[2]);
      if (m[3]) args.push("--takeoff_height", m[3]);
      await invokeComp("droneCommand", { action: "runMain", args });
      return setResponse(`Hover: ${m[1]}`);
    }

    // Circle
    if (/fly in a circle/.test(cmd)) {
      await invokeComp("droneCommand", {
        action: "runMain",
        args: [
          "--config",
          "scripted_flight/config/drones.json",
          "--demo",
          "circle",
        ],
      });
      return setResponse("Circle demo");
    }

    // V-Formation
    if ((m = cmd.match(/v formation with drone (\d+)/))) {
      const leader = `E${m[1]}`;
      await invokeComp("droneCommand", {
        action: "runMain",
        args: [
          "--config",
          "scripted_flight/config/drones.json",
          "--demo",
          "v",
          "--leader",
          leader,
        ],
      });
      return setResponse(`V formation around drone ${m[1]}`);
    }

    // Surround
    if ((m = cmd.match(/surround drone (\d+)/))) {
      const leader = `E${m[1]}`;
      await invokeComp("droneCommand", {
        action: "runMain",
        args: [
          "--config",
          "scripted_flight/config/drones.json",
          "--demo",
          "surround",
          "--leader",
          leader,
        ],
      });
      return setResponse(`Surround drone ${m[1]}`);
    }

    // Reset
    if (/reset(?: all)? drones?/.test(cmd)) {
      const body = cmd.includes("all")
        ? { action: "reset", config: "scripted_flight/config/drones.json" }
        : {
            action: "reset",
            uri: `radio://…E${cmd.match(/drone (\d+)/)![1]}`,
          };
      await invokeComp("droneCommand", body);
      return setResponse("Reset executed");
    }

    // AI fallback
    setResponse("Generating code…");
    const ai = await axios.post("/api/cerebras", {
      prompt: `Implement: "${cmd}" in scripted_flight/`,
      max_tokens: 300,
      temperature: 0.7,
    });
    const code =
      ai.data.choices?.[0]?.message?.content ?? ai.data.choices?.[0]?.text;
    setGeneratedCode(code);
    setShowRun(true);
    setResponse("Code ready. Run?");
  }, []);

  const runCode = async () => {
    await invokeComp("executeCode", { code: generatedCode });
    setResponse("Code executed.");
    setShowRun(false);
    setGeneratedCode("");
  };

  // don’t render until hydration
  if (!mounted) return null;

  return (
    <ChakraProvider>
      <Box
        position="relative"
        w="100vw"
        h="100vh"
        bg={theme === "dark" ? "#111" : "#eef"}
      >
        {/* You can re-add an Orb or other visual here if you like */}

        <IconButton
          aria-label="Open settings"
          icon={<FaCog />}
          onClick={() => setSettingsOpen(true)}
          position="absolute"
          top={2}
          right={2}
        />

        <Flex direction="column" align="center" justify="end" h="100%" pb={10}>
          {transcript && (
            <Box mb={2} bg="rgba(0,0,0,0.5)" color="white" p={2} borderRadius="md">
              Hearing: {transcript}
            </Box>
          )}
          {response && (
            <Box mb={4} bg="rgba(0,0,0,0.7)" color="cyan.200" p={3} borderRadius="md">
              Miso: {response}
            </Box>
          )}
          {showRun && (
            <Button onClick={runCode} colorScheme="green" mb={4}>
              Run Code
            </Button>
          )}

          <Flex gap={4}>
            <TutorialTooltip content="Start listening">
              <IconButton
                aria-label="Start listening"
                icon={<FaMicrophone />}
                onClick={startListening}
              />
            </TutorialTooltip>
            <TutorialTooltip content="Stop listening">
              <IconButton
                aria-label="Stop listening"
                icon={<FaStop />}
                onClick={stopListening}
              />
            </TutorialTooltip>
          </Flex>
        </Flex>

        <SettingsModal
          isOpen={isSettingsOpen}
          onClose={() => setSettingsOpen(false)}
          auraColor={auraColor}
          setAuraColor={setAuraColor}
          voiceSpeed={voiceSpeed}
          setVoiceSpeed={setVoiceSpeed}
          theme={theme}
          setTheme={setTheme}
          cerebrasKey={cerebrasKey}
          setCerebrasKey={setCerebrasKey}
        />
      </Box>
    </ChakraProvider>
  );
}
