import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Send, Settings, Layers } from "lucide-react";

import { FrameworkSelector } from "./framework_selector";
import { MultiFrameworkProgress } from "./multi_framework_progress";
import { RFEBuilderProgress } from "./rfe_builder_progress";

export function EnhancedRFEBuilder({ 
  onSubmit,
  onFrameworkStop,
  onFrameworkRestart,
  onOpenHandsTrigger,
  initialFrameworks = ["llamaindex"]
}) {
  const [userInput, setUserInput] = useState("");
  const [selectedFrameworks, setSelectedFrameworks] = useState(initialFrameworks);
  const [isExecuting, setIsExecuting] = useState(false);
  const [frameworkEvents, setFrameworkEvents] = useState({});
  const [phase1Complete, setPhase1Complete] = useState(false);
  const [artifacts, setArtifacts] = useState({});
  const [viewMode, setViewMode] = useState("side-by-side"); // or "tabbed"
  const [showSettings, setShowSettings] = useState(false);

  const handleSubmit = async () => {
    if (!userInput.trim() || selectedFrameworks.length === 0) return;
    
    setIsExecuting(true);
    setFrameworkEvents({});
    
    // Initialize event tracking for each framework
    const initialEvents = {};
    selectedFrameworks.forEach(framework => {
      initialEvents[framework] = [];
    });
    setFrameworkEvents(initialEvents);
    
    // Submit to backend with framework selection
    try {
      await onSubmit({
        user_input: userInput,
        frameworks: selectedFrameworks,
        multi_framework_mode: selectedFrameworks.length > 1
      });
    } catch (error) {
      console.error("Submission error:", error);
    }
  };

  const handleFrameworksChange = (frameworks) => {
    setSelectedFrameworks(frameworks);
    
    // Reset events for deselected frameworks
    const newEvents = {};
    frameworks.forEach(framework => {
      newEvents[framework] = frameworkEvents[framework] || [];
    });
    setFrameworkEvents(newEvents);
  };

  const handleFrameworkStop = async (framework) => {
    try {
      await onFrameworkStop(framework);
      
      // Update framework events to show stopped state
      setFrameworkEvents(prev => ({
        ...prev,
        [framework]: [
          ...prev[framework],
          {
            type: "stopped",
            data: { message: `${framework} stopped by user` }
          }
        ]
      }));
    } catch (error) {
      console.error(`Error stopping ${framework}:`, error);
    }
  };

  const handleFrameworkRestart = async (framework) => {
    try {
      // Clear previous events for this framework
      setFrameworkEvents(prev => ({
        ...prev,
        [framework]: []
      }));
      
      await onFrameworkRestart(framework, userInput);
    } catch (error) {
      console.error(`Error restarting ${framework}:`, error);
    }
  };

  const handleOpenHandsTrigger = async () => {
    if (!phase1Complete || !artifacts) return;
    
    try {
      await onOpenHandsTrigger(artifacts);
    } catch (error) {
      console.error("Error triggering OpenHands:", error);
    }
  };

  // Subscribe to workflow events
  useEffect(() => {
    const handleWorkflowEvent = (event) => {
      const { type, data } = event;
      
      // Route events to appropriate framework
      if (data?.framework) {
        setFrameworkEvents(prev => ({
          ...prev,
          [data.framework]: [...(prev[data.framework] || []), event]
        }));
      }
      
      // Check for phase completion
      if (type === "phase_1_ready" || type === "artifacts_complete") {
        setPhase1Complete(true);
        setArtifacts(data.artifacts || {});
      }
      
      // Handle workflow completion
      if (type === "workflow_complete" || type === "multi_framework_complete") {
        setIsExecuting(false);
      }
    };

    // Subscribe to events (implementation depends on your event system)
    // window.addEventListener("workflow_event", handleWorkflowEvent);
    
    return () => {
      // window.removeEventListener("workflow_event", handleWorkflowEvent);
    };
  }, []);

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Enhanced RFE Builder</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Settings className="h-4 w-4 mr-1" />
              Settings
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Describe your feature request or enhancement..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            className="min-h-[120px]"
            disabled={isExecuting}
          />
          
          {showSettings && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
              <FrameworkSelector
                selectedFrameworks={selectedFrameworks}
                onFrameworksChange={handleFrameworksChange}
                disabled={isExecuting}
              />
              
              <div className="flex items-center gap-4">
                <label className="text-sm font-medium">View Mode:</label>
                <div className="flex gap-2">
                  <Button
                    variant={viewMode === "side-by-side" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("side-by-side")}
                    disabled={isExecuting}
                  >
                    <Layers className="h-4 w-4 mr-1" />
                    Side-by-Side
                  </Button>
                  <Button
                    variant={viewMode === "tabbed" ? "default" : "outline"}
                    size="sm"
                    onClick={() => setViewMode("tabbed")}
                    disabled={isExecuting}
                  >
                    Tabbed
                  </Button>
                </div>
              </div>
            </div>
          )}
          
          <Button 
            onClick={handleSubmit}
            disabled={isExecuting || !userInput.trim() || selectedFrameworks.length === 0}
            className="w-full"
          >
            <Send className="h-4 w-4 mr-2" />
            {isExecuting ? "Processing..." : "Submit RFE"}
          </Button>
        </CardContent>
      </Card>

      {/* Progress Section */}
      {(isExecuting || Object.keys(frameworkEvents).length > 0) && (
        <>
          {selectedFrameworks.length === 1 && selectedFrameworks[0] === "llamaindex" ? (
            // Single LlamaIndex mode - use existing progress component
            <RFEBuilderProgress events={frameworkEvents["llamaindex"] || []} />
          ) : (
            // Multi-framework mode - use new progress component
            <MultiFrameworkProgress
              events={frameworkEvents}
              onStopFramework={handleFrameworkStop}
              onRestartFramework={handleFrameworkRestart}
              onTriggerOpenHands={handleOpenHandsTrigger}
              activeFrameworks={selectedFrameworks}
              phase1Complete={phase1Complete}
              viewMode={viewMode}
            />
          )}
        </>
      )}

      {/* Framework Comparison Summary */}
      {!isExecuting && selectedFrameworks.length > 1 && Object.keys(frameworkEvents).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Framework Comparison Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {selectedFrameworks.map(framework => {
                const events = frameworkEvents[framework] || [];
                const hasError = events.some(e => e.type === "error");
                const isComplete = events.some(e => e.type === "complete");
                const artifactCount = events.filter(e => e.data?.artifacts).length;
                
                return (
                  <div key={framework} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium">{framework.toUpperCase()}</span>
                      <div className="text-sm text-gray-600 mt-1">
                        Events: {events.length} | Artifacts: {artifactCount}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {hasError && (
                        <Badge variant="destructive">Error</Badge>
                      )}
                      {isComplete && (
                        <Badge variant="success">Complete</Badge>
                      )}
                      {!hasError && !isComplete && events.length > 0 && (
                        <Badge variant="secondary">In Progress</Badge>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
            
            <Alert className="mt-4">
              <AlertDescription>
                Framework bakeoff mode enabled. Compare how different frameworks approach your RFE refinement.
                Each framework processes independently with continue-on-error behavior.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
}