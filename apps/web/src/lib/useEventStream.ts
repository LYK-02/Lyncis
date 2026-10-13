"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Event, VesselTrack, ReplayStatus } from "@/types/events";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/events";

export function useEventStream() {
  const [events, setEvents] = useState<Event[]>([]);
  const [vessels, setVessels] = useState<VesselTrack[]>([]);
  const [replayStatus, setReplayStatus] = useState<ReplayStatus | null>(null);
  const [connectionState, setConnectionState] = useState<"connecting" | "live" | "replay" | "offline">("connecting");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    setConnectionState("connecting");
    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttemptsRef.current = 0;
        setConnectionState("live");
      };

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === "hello") {
            if (msg.data.recent_events) {
              setEvents(msg.data.recent_events);
            }
            if (msg.data.vessels) {
              setVessels(msg.data.vessels);
            }
            if (msg.data.replay) {
              setReplayStatus(msg.data.replay);
              setConnectionState(msg.data.replay.is_playing ? "replay" : "live");
            }
          } else if (msg.type === "event") {
            const newEvent: Event = msg.data;
            setEvents((prev) => {
              // Avoid duplicates
              if (prev.some((item) => item.id === newEvent.id)) return prev;
              return [newEvent, ...prev].slice(0, 200); // Keep last 200
            });
            if (msg.vessels) {
              setVessels(msg.vessels);
            }
          } else if (msg.type === "heartbeat") {
            if (msg.replay) {
              setReplayStatus(msg.replay);
              if (msg.replay.is_playing) {
                setConnectionState("replay");
              }
            }
            if (msg.vessels) {
              setVessels(msg.vessels);
            }
          }
        } catch (err) {
          console.error("Failed to parse WS message", err);
        }
      };

      ws.onclose = () => {
        setConnectionState("offline");
        // Reconnect with backoff
        const timeout = Math.min(30000, 1000 * Math.pow(1.5, reconnectAttemptsRef.current));
        reconnectAttemptsRef.current += 1;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, timeout);
      };

      ws.onerror = () => {
        ws.close();
      };
    } catch {
      setConnectionState("offline");
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connect]);

  return {
    events,
    vessels,
    replayStatus,
    connectionState,
    reconnect: connect,
  };
}
