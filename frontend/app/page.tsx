"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Download, Copy, FileText, Loader2, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function YouTubeNotesConverter() {
  const [videoUrl, setVideoUrl] = useState("");
  const [isConverting, setIsConverting] = useState(false);
  const [notes, setNotes] = useState("");
  const { toast } = useToast();

  const handleConvert = async () => {
    if (!videoUrl.trim()) {
      toast({
        title: "Please enter a YouTube URL",
        description:
          "A valid YouTube video URL is required to generate notes.",
        variant: "destructive",
      });
      return;
    }

    setIsConverting(true);

    try {
      const res = await fetch("http://localhost:8000/generate-notes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: videoUrl }),
      });

      if (!res.ok) throw new Error("Failed to generate notes");

      const data = await res.json();
      setNotes(data.markdown);

      toast({
        title: "Notes generated successfully!",
        description: "Your study notes are ready for download or editing.",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "Conversion failed",
        description:
          "There was an error processing your video. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsConverting(false);
    }
  };

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(notes);
    toast({
      title: "Copied to clipboard!",
      description: "Markdown notes have been copied to your clipboard.",
    });
  };

  const handleDownloadPDF = async () => {
    if (!notes.trim()) {
      toast({
        title: "No notes to download",
        description: "Please generate notes first.",
        variant: "destructive",
      });
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/generate-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ markdown: notes }),
      });

      if (!res.ok) throw new Error("Failed to generate PDF");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "notes.pdf";
      a.click();

      window.URL.revokeObjectURL(url);

      toast({
        title: "PDF downloaded",
        description: "Your notes are saved as PDF with proper formatting.",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "Download failed",
        description: "Could not generate PDF. Try again later.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <FileText className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">LectureLM</h1>
              <p className="text-sm text-slate-600">YouTube Lectures to Notes</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-16 max-w-4xl">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 text-balance">
            Transform YouTube Lectures
            <br />
            <span className="text-blue-600">into Revision Notes</span>
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Convert any YouTube lecture into comprehensive, AI-generated markdown
            notes with video citations. Perfect for revising online course content.
          </p>
        </div>

        <Card className="mb-12 shadow-sm border-0 bg-white">
          <CardHeader>
            <CardTitle className="text-xl text-slate-900">
              Convert Video
            </CardTitle>
            <CardDescription>
              Paste a YouTube URL to generate revision notes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-3">
              <Input
                placeholder="https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="flex-1 h-11"
                disabled={isConverting}
              />
              <Button
                onClick={handleConvert}
                disabled={isConverting}
                className="h-11 px-6 bg-blue-600 hover:bg-blue-700"
              >
                {isConverting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Converting...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Convert
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {notes && (
          <Card className="shadow-sm border-0 bg-white">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl text-slate-900">
                    Your Notes
                  </CardTitle>
                  <CardDescription>
                    Edit your notes below or download as PDF
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleCopyMarkdown}
                    className="h-9 bg-transparent"
                  >
                    <Copy className="h-4 w-4 mr-2" />
                    Copy
                  </Button>
                  <Button
                    onClick={handleDownloadPDF}
                    className="h-9 bg-blue-600 hover:bg-blue-700"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    PDF
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="min-h-[400px] font-mono text-sm resize-none"
                placeholder="Your AI-generated notes will appear here..."
              />
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
