"use client";

import { useState, useMemo, useEffect } from "react";
import { useEventStream } from "@/lib/useEventStream";
import { fetchSources, startReplay, pauseReplay, seekReplay, resetReplay } from "@/lib/api";
import { Event, SourceHealth } from "@/types/events";
import { TopBar } from "@/components/TopBar";
import { FilterRail } from "@/components/FilterRail";
import { MapConsole } from "@/components/MapConsole";
import { EventFeed } from "@/components/EventFeed";
import { EventDrawer } from "@/components/EventDrawer";
import { ReplayBar } from "@/components/ReplayBar";

export default function ConsolePage() {
  const { events, vessels, replayStatus, connectionState } = useEventStream();
  const [sources, setSources] = useState<SourceHealth[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  // Filters
  const [selectedModule, setSelectedModule] = useState("all");
  const [selectedSeverity, setSelectedSeverity] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch source health on load
  useEffect(() => {
    fetchSources()
      .then(setSources)
      .catch((err) => console.error("Error fetching sources:", err));
  }, []);

  // Keyboard navigation per 06-APPFLOW.md §8
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setSelectedEvent(null);
      } else if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        if (replayStatus?.is_playing) {
          pauseReplay();
        } else {
          startReplay(replayStatus?.speed || 5.0);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [replayStatus]);

  // Filtered Events
  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      if (selectedModule !== "all" && ev.source !== selectedModule) return false;
      if (selectedSeverity !== "all" && ev.severity !== selectedSeverity) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = ev.title.toLowerCase().includes(q);
        const matchesEntity = (ev.entity_name || "").toLowerCase().includes(q) || (ev.entity_id || "").toLowerCase().includes(q);
        if (!matchesTitle && !matchesEntity) return false;
      }
      return true;
    });
  }, [events, selectedModule, selectedSeverity, searchQuery]);

  // Statistics
  const stats = useMemo(() => {
    let high = 0;
    let gaps = 0;
    let sanctions = 0;
    events.forEach((ev) => {
      if (ev.severity === "high") high++;
      if (ev.type === "ais_gap") gaps++;
      if (ev.type === "sanctions_match") sanctions++;
    });
    return {
      totalEvents: events.length,
      highSeverity: high,
      activeGaps: gaps,
      sanctionMatches: sanctions,
    };
  }, [events]);

  const handleSelectVessel = (mmsi: string) => {
    const related = events.find((e) => e.entity_id === mmsi);
    if (related) {
      setSelectedEvent(related);
    }
  };

  const handleSelectParent = (parentId: string) => {
    const parent = events.find((e) => e.id === parentId);
    if (parent) {
      setSelectedEvent(parent);
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#050505] text-white">
      {/* 1. Header TopBar */}
      <TopBar
        mode={connectionState}
        sources={sources}
        onToggleReplay={() => {
          if (replayStatus?.is_playing) {
            pauseReplay();
          } else {
            startReplay(5.0);
          }
        }}
      />

      {/* 2. Main Console Grid */}
      <div className="flex flex-1 overflow-hidden relative">
        {/* Left Filter Rail */}
        <FilterRail
          selectedModule={selectedModule}
          onSelectModule={setSelectedModule}
          selectedSeverity={selectedSeverity}
          onSelectSeverity={setSelectedSeverity}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          stats={stats}
        />

        {/* Center Interactive Map */}
        <div className="flex-1 relative flex flex-col overflow-hidden">
          <MapConsole
            vessels={vessels}
            events={events}
            selectedEventId={selectedEvent?.id || null}
            onSelectVessel={handleSelectVessel}
          />
        </div>

        {/* Right Event Feed */}
        <EventFeed
          events={filteredEvents}
          selectedEventId={selectedEvent?.id || null}
          onSelectEvent={(ev) => setSelectedEvent(ev)}
        />

        {/* Sliding Detail Drawer */}
        <EventDrawer
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
          onSelectParent={handleSelectParent}
        />
      </div>

      {/* 3. Replay Control Bar */}
      <ReplayBar
        status={replayStatus}
        onPlay={(spd) => startReplay(spd)}
        onPause={() => pauseReplay()}
        onSeek={(sec) => seekReplay(sec)}
        onReset={() => resetReplay()}
        onSetSpeed={(spd) => startReplay(spd)}
      />
    </div>
  );
}
