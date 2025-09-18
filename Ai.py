import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';

const AI_Debate_App = () => {
  // Application states
  const [appState, setAppState] = useState<'topic-selection' | 'timer-setup' | 'debate' | 'summary'>('topic-selection');
  const [selectedTopic, setSelectedTopic] = useState<string>('');
  const [debateType, setDebateType] = useState<'predefined' | 'typed' | 'spoken'>('predefined');
  const [timerDuration, setTimerDuration] = useState<number>(180); // 3 minutes default
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [debateHistory, setDebateHistory] = useState<Array<{speaker: 'user' | 'ai', text: string, time: string}>>([]);
  const [summary, setSummary] = useState<{summary: string, winner: 'user' | 'ai' | 'draw', strengths: {
    user: {clarity: number, quality: number, persuasiveness: number},
    ai: {clarity: number, quality: number, persuasiveness: number}
  }} | null>(null);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Predefined debate topics
  const predefinedTopics = [
    { id: 1, title: "AI's Impact on Employment", description: "Debate whether AI will create more jobs than it displaces" },
    { id: 2, title: "Universal Basic Income", description: "Discuss the merits and drawbacks of UBI in modern economies" },
    { id: 3, title: "Climate Change Action", description: "Debate the most effective approaches to combat climate change" },
    { id: 4, title: "Social Media Regulation", description: "Discuss if and how social media platforms should be regulated" }
  ];

  // Start a new debate
  const startDebate = () => {
    setAppState('debate');
    setTimeRemaining(timerDuration);
    setDebateHistory([]);
    
    // Start timer
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          endDebate();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    
    // AI starts the debate with an opening statement (simulated)
    const openingStatement = "Thank you for initiating this debate. I'm looking forward to a thoughtful discussion on this topic. Let's begin.";
    addDebateTurn('ai', openingStatement);
    
    // Simulate TTS playback (in a real app, this would use Google TTS)
    if (audioRef.current) {
      audioRef.current.src = "https://placeholder-audio-service.onrender.com/audio/5?prompt=AI%20opening%20statement%20for%20debate&id=d67e8a13-f9d4-43f2-a927-eb55cffc8bea&customer_id=cus_T1S5cK6ZRJV3bZ";
      audioRef.current.play().catch(e => console.log("Audio play failed:", e));
    }
  };

  // Add a turn to the debate history
  const addDebateTurn = (speaker: 'user' | 'ai', text: string) => {
    const now = new Date();
    const timeString = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    setDebateHistory(prev => [...prev, { speaker, text, time: timeString }]);
  };

  // Handle user speech input
  const handleUserSpeech = () => {
    setIsRecording(true);
    
    // In a real app, this would use Web Speech API to capture speech
    // For this demo, we'll simulate speech recognition after a delay
    setTimeout(() => {
      const simulatedResponse = "I believe that while technology brings many benefits, we must be cautious about its ethical implications and societal impact.";
      addDebateTurn('user', simulatedResponse);
      setIsRecording(false);
      
      // Simulate AI response after a short delay
      setTimeout(() => {
        const aiResponse = "That's a valid concern. However, history shows that technological progress ultimately creates more opportunities than it eliminates. For instance, the industrial revolution initially displaced workers but eventually led to higher living standards.";
        addDebateTurn('ai', aiResponse);
        
        // Simulate TTS playback for AI response
        if (audioRef.current) {
          audioRef.current.src = "https://placeholder-audio-service.onrender.com/audio/10?prompt=AI%20counterargument%20in%20debate&id=d67e8a13-f9d4-43f2-a927-eb55cffc8bea&customer_id=cus_T1S5cK6ZRJV3bZ";
          audioRef.current.play().catch(e => console.log("Audio play failed:", e));
        }
      }, 2000);
    }, 3000);
  };

  // End the debate
  const endDebate = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    // Generate summary and analysis (simulated)
    const generatedSummary = {
      summary: "The debate centered around the impact of technology on society. The user raised concerns about ethical implications, while the AI argued that technological progress ultimately benefits society. Both sides presented reasonable arguments, with the AI providing more historical evidence to support its claims.",
      winner: 'ai' as const,
      strengths: {
        user: { clarity: 8, quality: 7, persuasiveness: 6 },
        ai: { clarity: 9, quality: 9, persuasiveness: 8 }
      }
    };
    
    setSummary(generatedSummary);
    setAppState('summary');
  };

  // Reset the app to start a new debate
  const resetApp = () => {
    setAppState('topic-selection');
    setSelectedTopic('');
    setDebateType('predefined');
    setTimerDuration(180);
    setTimeRemaining(0);
    setDebateHistory([]);
    setSummary(null);
  };

  // Format time for display (MM:SS)
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4 md:p-8">
      {/* Hidden audio element for TTS playback */}
      <audio ref={audioRef} className="hidden" />
      
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900 mb-2"
          >
            AI Debate Platform
          </motion.h1>
          <p className="text-gray-600">Test your arguments against an AI opponent</p>
        </header>

        <main>
          {/* Topic Selection Screen */}
          {appState === 'topic-selection' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Choose a Debate Topic</CardTitle>
                  <CardDescription>Select from predefined topics or create your own</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {predefinedTopics.map(topic => (
                      <motion.div
                        key={topic.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Card 
                          className={`cursor-pointer transition-all ${selectedTopic === topic.title ? 'border-primary ring-2 ring-primary/20' : ''}`}
                          onClick={() => {
                            setSelectedTopic(topic.title);
                            setDebateType('predefined');
                          }}
                        >
                          <CardHeader className="pb-3">
                            <CardTitle className="text-lg">{topic.title}</CardTitle>
                            <CardDescription>{topic.description}</CardDescription>
                          </CardHeader>
                        </Card>
                      </motion.div>
                    ))}
                  </div>

                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="custom-topic" className="text-lg font-medium">Or Type Your Own Topic</Label>
                      <Input
                        id="custom-topic"
                        placeholder="Enter your debate topic"
                        className="mt-2"
                        value={debateType === 'typed' ? selectedTopic : ''}
                        onChange={(e) => {
                          setSelectedTopic(e.target.value);
                          setDebateType('typed');
                        }}
                      />
                    </div>

                    <div>
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => {
                          // In a real app, this would use Web Speech API
                          setSelectedTopic("Technology's impact on society");
                          setDebateType('spoken');
                        }}
                      >
                        <img 
                          src="https://placeholder-image-service.onrender.com/image/24x24?prompt=Microphone%20icon%20for%20voice%20input&id=d67e8a13-f9d4-43f2-a927-eb55cffc8bea&customer_id=cus_T1S5cK6ZRJV3bZ" 
                          alt="Microphone icon for voice input"
                          className="mr-2"
                        />
                        Speak Your Topic
                      </Button>
                      {debateType === 'spoken' && (
                        <p className="mt-2 text-sm text-muted-foreground">Selected: "{selectedTopic}"</p>
                      )}
                    </div>
                  </div>

                  <Button 
                    className="w-full mt-4" 
                    disabled={!selectedTopic}
                    onClick={() => setAppState('timer-setup')}
                  >
                    Continue to Timer Setup
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Timer Setup Screen */}
          {appState === 'timer-setup' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Card>
                <CardHeader>
                  <CardTitle>Set Debate Timer</CardTitle>
                  <CardDescription>How long would you like the debate to last?</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="debate-timer" className="text-lg font-medium">Debate Duration (minutes)</Label>
                      <Input
                        id="debate-timer"
                        type="number"
                        min="1"
                        max="60"
                        value={Math.floor(timerDuration / 60)}
                        onChange={(e) => setTimerDuration(parseInt(e.target.value) * 60)}
                        className="mt-2"
                      />
                    </div>
                    
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="font-medium">Selected Topic:</p>
                      <p className="text-lg">"{selectedTopic}"</p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <Button variant="outline" onClick={() => setAppState('topic-selection')}>
                      Back
                    </Button>
                    <Button onClick={startDebate}>
                      Start Debate
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Debate Screen */}
          {appState === 'debate' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                  <div>
                    <CardTitle>Live Debate</CardTitle>
                    <CardDescription>Topic: {selectedTopic}</CardDescription>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="bg-primary/10 text-primary font-mono font-bold text-xl px-3 py-1 rounded">
                      {formatTime(timeRemaining)}
                    </div>
                    <Button variant="outline" onClick={endDebate}>
                      End Debate
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="border rounded-lg bg-white p-4 h-96 overflow-y-auto space-y-4">
                    <AnimatePresence>
                      {debateHistory.map((turn, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`flex ${turn.speaker === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs md:max-w-md rounded-lg p-3 ${turn.speaker === 'user' 
                              ? 'bg-primary text-primary-foreground rounded-br-none' 
                              : 'bg-muted rounded-bl-none'
                            }`}
                          >
                            <p className="text-sm">{turn.text}</p>
                            <p className={`text-xs mt-1 ${turn.speaker === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                              {turn.time} • {turn.speaker === 'user' ? 'You' : 'AI'}
                            </p>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </div>

                  <div className="mt-6 flex justify-center">
                    <Button
                      onClick={handleUserSpeech}
                      disabled={isRecording}
                      className="flex items-center gap-2"
                    >
                      {isRecording ? (
                        <>
                          <div className="w-4 h-4 rounded-full bg-destructive animate-pulse"></div>
                          Listening...
                        </>
                      ) : (
                        <>
                          <img 
                            src="https://placeholder-image-service.onrender.com/image/24x24?prompt=Microphone%20icon%20for%20voice%20input&id=d67e8a13-f9d4-43f2-a927-eb55cffc8bea&customer_id=cus_T1S5cK6ZRJV3bZ" 
                            alt="Microphone icon for voice input"
                          />
                          Speak Your Argument
                        </>
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Summary Screen */}
          {appState === 'summary' && summary && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle>Debate Summary</CardTitle>
                  <CardDescription>Analysis of your debate performance</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="text-center py-4">
                    <div className="inline-flex items-center justify-center bg-muted px-4 py-2 rounded-full">
                      <span className="text-lg font-semibold">Topic:</span>
                      <span className="ml-2 text-lg">{selectedTopic}</span>
                    </div>
                  </div>

                  <div className={`p-6 rounded-lg text-center ${summary.winner === 'user' 
                    ? 'bg-green-50 border border-green-200' 
                    : summary.winner === 'ai' 
                      ? 'bg-blue-50 border border-blue-200' 
                      : 'bg-yellow-50 border border-yellow-200'
                  }`}>
                    <h3 className="text-2xl font-bold mb-2">Debate Result</h3>
                    <div className="text-4xl font-bold mb-2">
                      {summary.winner === 'user' ? '🎉 You Won!' : summary.winner === 'ai' ? '🤖 AI Won' : '🤝 Draw'}
                    </div>
                    <p className="text-muted-foreground">
                      {summary.winner === 'user' 
                        ? 'Congratulations! Your arguments were more persuasive.' 
                        : summary.winner === 'ai' 
                          ? 'The AI had stronger arguments this time. Try again!'
                          : 'The debate ended in a draw. Both sides presented compelling arguments.'
                      }
                    </p>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-4">Argument Strength Analysis</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="border rounded-lg p-4">
                        <h4 className="font-medium text-lg mb-3">Your Arguments</h4>
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Clarity</span>
                              <span>{summary.strengths.user.clarity}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-primary h-full rounded-full" 
                                style={{ width: `${summary.strengths.user.clarity * 10}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Quality</span>
                              <span>{summary.strengths.user.quality}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-primary h-full rounded-full" 
                                style={{ width: `${summary.strengths.user.quality * 10}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Persuasiveness</span>
                              <span>{summary.strengths.user.persuasiveness}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-primary h-full rounded-full" 
                                style={{ width: `${summary.strengths.user.persuasiveness * 10}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="border rounded-lg p-4">
                        <h4 className="font-medium text-lg mb-3">AI Arguments</h4>
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Clarity</span>
                              <span>{summary.strengths.ai.clarity}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-blue-500 h-full rounded-full" 
                                style={{ width: `${summary.strengths.ai.clarity * 10}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Quality</span>
                              <span>{summary.strengths.ai.quality}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-blue-500 h-full rounded-full" 
                                style={{ width: `${summary.strengths.ai.quality * 10}%` }}
                              ></div>
                            </div>
                          </div>
                          <div>
                            <div className="flex justify-between mb-1">
                              <span>Persuasiveness</span>
                              <span>{summary.strengths.ai.persuasiveness}/10</span>
                            </div>
                            <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-blue-500 h-full rounded-full" 
                                style={{ width: `${summary.strengths.ai.persuasiveness * 10}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold mb-3">Debate Summary</h3>
                    <div className="bg-muted p-4 rounded-lg">
                      <p>{summary.summary}</p>
                    </div>
                  </div>

                  <div className="flex justify-center pt-4">
                    <Button onClick={resetApp}>
                      Start New Debate
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AI_Debate_App;
