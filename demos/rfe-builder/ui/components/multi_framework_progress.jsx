import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  StopCircle, 
  PlayCircle, 
  CheckCircle2, 
  AlertCircle,
  Loader2,
  Code,
  Brain,
  Users,
  Layers,
  XCircle
} from "lucide-react";

const FRAMEWORK_ICONS = {
  llamaindex: Brain,
  openhands: Code,
  langchain: Layers,
  crewai: Users
};

const FRAMEWORK_COLORS = {
  llamaindex: "blue",
  openhands: "green",
  langchain: "purple",
  crewai: "orange"
};

function FrameworkProgressPanel({ 
  framework, 
  events = [], 
  onStop, 
  onRestart,
  showStopButton = true,
  isRunning = false,
  hasError = false
}) {
  const [expanded, setExpanded] = useState(true);
  const [currentPhase, setCurrentPhase] = useState("initializing");
  const [progress, setProgress] = useState(0);
  const [streamingContent, setStreamingContent] = useState("");

  const Icon = FRAMEWORK_ICONS[framework] || Brain;
  const color = FRAMEWORK_COLORS[framework] || "gray";

  useEffect(() => {
    // Process events to determine current phase and progress
    if (events.length > 0) {
      const lastEvent = events[events.length - 1];
      const eventData = lastEvent.data || {};
      
      if (eventData.phase) {
        setCurrentPhase(eventData.phase);
      }
      
      // Calculate progress based on event types
      const completeEvents = events.filter(e => e.type === "complete").length;
      const totalExpectedPhases = 5; // Adjust based on workflow
      setProgress((completeEvents / totalExpectedPhases) * 100);
      
      // Handle streaming content
      if (lastEvent.type === "streaming" && eventData.message) {
        setStreamingContent(eventData.message);
      }
    }
  }, [events]);

  const getStatusBadge = () => {
    if (hasError) {
      return <Badge variant="destructive">Error</Badge>;
    }
    if (!isRunning && events.length === 0) {
      return <Badge variant="outline">Ready</Badge>;
    }
    if (!isRunning && events.length > 0) {
      return <Badge variant="default">Complete</Badge>;
    }
    return <Badge className={`bg-${color}-500`}>Running</Badge>;
  };

  const getPhaseDisplay = () => {
    const phaseMap = {
      initializing: "Initializing",
      analysis: "Analyzing",
      synthesis: "Synthesizing",
      artifact_generation: "Generating Artifacts",
      complete: "Complete",
      error: "Error Occurred"
    };
    return phaseMap[currentPhase] || currentPhase;
  };

  return (
    <Card className={`h-full border-2 ${hasError ? 'border-red-300' : `border-${color}-200`}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className={`h-5 w-5 text-${color}-500`} />
            <CardTitle className="text-base">{framework.toUpperCase()}</CardTitle>
            {getStatusBadge()}
          </div>
          <div className="flex items-center gap-2">
            {showStopButton && isRunning && (
              <Button
                size="sm"
                variant="outline"
                onClick={onStop}
                className="h-7"
              >
                <StopCircle className="h-4 w-4 mr-1" />
                Stop
              </Button>
            )}
            {!isRunning && hasError && (
              <Button
                size="sm"
                variant="outline"
                onClick={onRestart}
                className="h-7"
              >
                <PlayCircle className="h-4 w-4 mr-1" />
                Retry
              </Button>
            )}
          </div>
        </div>
        
        {isRunning && (
          <div className="mt-3 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">{getPhaseDisplay()}</span>
              <span className="text-gray-500">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}
      </CardHeader>
      
      <CardContent className="pt-0">
        {hasError && (
          <Alert variant="destructive" className="mb-3">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {events.find(e => e.data?.error)?.data?.error || "An error occurred during execution"}
            </AlertDescription>
          </Alert>
        )}
        
        <ScrollArea className="h-64">
          <div className="space-y-2">
            {isRunning && streamingContent && (
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm font-medium">Processing</span>
                </div>
                <p className="text-sm text-gray-600">{streamingContent}</p>
              </div>
            )}
            
            {events.map((event, idx) => (
              <FrameworkEventItem 
                key={idx} 
                event={event} 
                framework={framework}
                color={color}
              />
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}

function FrameworkEventItem({ event, framework, color }) {
  const { type, data = {} } = event;
  const { phase, agent, message, analysis, synthesis, artifacts } = data;
  
  const getEventIcon = () => {
    if (type === "error") return <XCircle className="h-4 w-4 text-red-500" />;
    if (type === "complete") return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    if (type === "streaming") return <Loader2 className="h-4 w-4 animate-spin" />;
    return <AlertCircle className="h-4 w-4 text-gray-400" />;
  };
  
  return (
    <div className="p-2 border rounded-lg bg-white">
      <div className="flex items-start gap-2">
        {getEventIcon()}
        <div className="flex-1 min-w-0">
          {agent && (
            <div className="text-xs text-gray-500 mb-1">
              Agent: {agent}
            </div>
          )}
          {message && (
            <p className="text-sm text-gray-700">{message}</p>
          )}
          {analysis && (
            <div className="mt-2 p-2 bg-blue-50 rounded text-xs">
              <span className="font-medium">Analysis:</span> {
                typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2)
              }
            </div>
          )}
          {synthesis && (
            <div className="mt-2 p-2 bg-purple-50 rounded text-xs">
              <span className="font-medium">Synthesis:</span> {
                typeof synthesis === 'string' ? synthesis : JSON.stringify(synthesis, null, 2)
              }
            </div>
          )}
          {artifacts && (
            <div className="mt-2 p-2 bg-green-50 rounded text-xs">
              <span className="font-medium">Artifacts Generated</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function MultiFrameworkProgress({ 
  events = {}, 
  onStopFramework,
  onRestartFramework,
  onTriggerOpenHands,
  activeFrameworks = [],
  phase1Complete = false,
  viewMode = "side-by-side" // "side-by-side" or "tabbed"
}) {
  const [selectedTab, setSelectedTab] = useState(activeFrameworks[0] || "llamaindex");
  
  // Group events by framework
  const frameworkStatuses = {};
  activeFrameworks.forEach(framework => {
    const frameworkEvents = events[framework] || [];
    const lastEvent = frameworkEvents[frameworkEvents.length - 1];
    
    frameworkStatuses[framework] = {
      events: frameworkEvents,
      isRunning: lastEvent?.type === "streaming",
      hasError: frameworkEvents.some(e => e.type === "error"),
      isComplete: lastEvent?.type === "complete"
    };
  });
  
  if (viewMode === "tabbed") {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Framework Execution Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${activeFrameworks.length}, 1fr)` }}>
              {activeFrameworks.map(framework => {
                const Icon = FRAMEWORK_ICONS[framework];
                const status = frameworkStatuses[framework];
                return (
                  <TabsTrigger key={framework} value={framework} className="flex items-center gap-2">
                    <Icon className="h-4 w-4" />
                    {framework}
                    {status.hasError && <XCircle className="h-3 w-3 text-red-500" />}
                    {status.isComplete && <CheckCircle2 className="h-3 w-3 text-green-500" />}
                  </TabsTrigger>
                );
              })}
            </TabsList>
            
            {activeFrameworks.map(framework => {
              const status = frameworkStatuses[framework];
              return (
                <TabsContent key={framework} value={framework}>
                  <FrameworkProgressPanel
                    framework={framework}
                    events={status.events}
                    onStop={() => onStopFramework(framework)}
                    onRestart={() => onRestartFramework(framework)}
                    showStopButton={framework !== "llamaindex"}
                    isRunning={status.isRunning}
                    hasError={status.hasError}
                  />
                </TabsContent>
              );
            })}
          </Tabs>
        </CardContent>
      </Card>
    );
  }
  
  // Side-by-side view
  return (
    <div className="w-full space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Framework Execution Progress</h3>
        <Badge variant="outline">
          {activeFrameworks.length} Frameworks Active
        </Badge>
      </div>
      
      <div className={`grid gap-4 ${
        activeFrameworks.length === 1 ? 'grid-cols-1' :
        activeFrameworks.length === 2 ? 'grid-cols-2' :
        'grid-cols-2 xl:grid-cols-3'
      }`}>
        {activeFrameworks.map(framework => {
          const status = frameworkStatuses[framework];
          return (
            <FrameworkProgressPanel
              key={framework}
              framework={framework}
              events={status.events}
              onStop={() => onStopFramework(framework)}
              onRestart={() => onRestartFramework(framework)}
              showStopButton={framework !== "llamaindex"}
              isRunning={status.isRunning}
              hasError={status.hasError}
            />
          );
        })}
      </div>
      
      {/* OpenHands Implementation Trigger */}
      {activeFrameworks.includes("openhands") && (
        <ImplementationTrigger
          onTrigger={onTriggerOpenHands}
          enabled={phase1Complete}
          frameworkStatus={frameworkStatuses["openhands"]}
        />
      )}
    </div>
  );
}

function ImplementationTrigger({ onTrigger, enabled, frameworkStatus }) {
  const isReady = enabled && frameworkStatus?.isComplete && !frameworkStatus?.hasError;
  
  return (
    <Card className="bg-green-50 border-green-200">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Code className="h-5 w-5 text-green-600" />
          OpenHands Implementation Phase
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <p className="text-sm text-gray-700">
            {isReady 
              ? "Phase 1 artifacts are ready. You can now trigger OpenHands to generate implementation plans and code."
              : "Complete Phase 1 RFE refinement to enable implementation generation."
            }
          </p>
          
          <Button 
            onClick={onTrigger}
            disabled={!isReady}
            className="w-full"
            variant={isReady ? "default" : "outline"}
          >
            <Code className="h-4 w-4 mr-2" />
            Start OpenHands Implementation
          </Button>
          
          {isReady && (
            <Alert className="bg-green-100 border-green-300">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>
                OpenHands will analyze your RFE artifacts and generate:
                <ul className="list-disc list-inside mt-2 text-sm">
                  <li>Implementation architecture and technical design</li>
                  <li>Sprint breakdown and development roadmap</li>
                  <li>Code scaffolding and project structure</li>
                  <li>API specifications and data models</li>
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}