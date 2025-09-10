import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Info } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const FRAMEWORKS = [
  {
    id: "llamaindex",
    name: "LlamaIndex",
    description: "Current workflow system with proven agent coordination",
    status: "default",
    badge: "Default",
    capabilities: ["Multi-agent analysis", "Artifact generation", "Production ready"],
    color: "bg-blue-50 border-blue-200"
  },
  {
    id: "openhands", 
    name: "OpenHands",
    description: "Code generation & task execution for implementation phase",
    status: "experimental",
    badge: "Implementation",
    capabilities: ["Code generation", "Task execution", "Implementation planning"],
    color: "bg-green-50 border-green-200"
  },
  {
    id: "langchain",
    name: "LangChain",
    description: "LangGraph workflows with agent tools and chains",
    status: "experimental",
    badge: "Experimental",
    capabilities: ["LangGraph", "Tool integration", "Agent chains"],
    color: "bg-purple-50 border-purple-200"
  },
  {
    id: "crewai",
    name: "CrewAI",
    description: "Hierarchical crew structure with collaborative agents",
    status: "experimental",
    badge: "Experimental",
    capabilities: ["Hierarchical crews", "Task delegation", "Collective decisions"],
    color: "bg-orange-50 border-orange-200"
  }
];

export function FrameworkSelector({ 
  selectedFrameworks = ["llamaindex"], 
  onFrameworksChange,
  disabled = false 
}) {
  const [selected, setSelected] = useState(new Set(selectedFrameworks));

  const handleFrameworkToggle = (frameworkId) => {
    if (disabled) return;
    
    const newSelected = new Set(selected);
    if (newSelected.has(frameworkId)) {
      // Don't allow deselecting LlamaIndex (always keep at least one)
      if (frameworkId === "llamaindex" && newSelected.size === 1) {
        return;
      }
      newSelected.delete(frameworkId);
    } else {
      newSelected.add(frameworkId);
    }
    
    setSelected(newSelected);
    if (onFrameworksChange) {
      onFrameworksChange(Array.from(newSelected));
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Framework Selection</CardTitle>
          <Badge variant="outline" className="ml-2">
            {selected.size} Active
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {FRAMEWORKS.map((framework) => {
            const isSelected = selected.has(framework.id);
            const isDefault = framework.id === "llamaindex";
            
            return (
              <div
                key={framework.id}
                className={`relative rounded-lg border-2 p-4 transition-all cursor-pointer ${
                  isSelected ? framework.color : "bg-gray-50 border-gray-200"
                } ${disabled ? "opacity-50 cursor-not-allowed" : "hover:shadow-md"}`}
                onClick={() => handleFrameworkToggle(framework.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Checkbox
                      checked={isSelected}
                      disabled={disabled || (isDefault && selected.size === 1)}
                      onClick={(e) => e.stopPropagation()}
                      onCheckedChange={() => handleFrameworkToggle(framework.id)}
                    />
                    <Label className="text-base font-semibold cursor-pointer">
                      {framework.name}
                    </Label>
                  </div>
                  <div className="flex items-center gap-1">
                    {framework.badge && (
                      <Badge 
                        variant={framework.status === "default" ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {framework.badge}
                      </Badge>
                    )}
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-4 w-4 text-gray-400" />
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          <p className="font-semibold mb-1">{framework.name}</p>
                          <p className="text-sm">{framework.description}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-3">
                  {framework.description}
                </p>
                
                <div className="flex flex-wrap gap-1">
                  {framework.capabilities.map((capability, idx) => (
                    <Badge 
                      key={idx} 
                      variant="outline" 
                      className="text-xs"
                    >
                      {capability}
                    </Badge>
                  ))}
                </div>
                
                {isDefault && selected.size === 1 && (
                  <div className="absolute inset-0 rounded-lg pointer-events-none">
                    <div className="absolute bottom-2 right-2">
                      <Badge variant="outline" className="text-xs bg-white">
                        Required
                      </Badge>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <span className="font-semibold">Framework Bakeoff Mode:</span> Select multiple frameworks to compare their approaches to RFE refinement side-by-side.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}