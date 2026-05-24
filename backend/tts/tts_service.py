"""Text-to-Speech service — edge-tts neural voices."""
import os
import re
import asyncio
import tempfile
from pathlib import Path
from typing import Optional


class TTSService:
    """
    Convert text to MP3 using Microsoft Edge TTS (zh-CN-YunxiNeural).
    YunxiNeural is a warm, natural male voice ideal for storytelling podcasts.
    Falls back to gTTS if edge-tts fails.
    """

    def __init__(self, provider: str = "edge"):
        self.provider = provider
        self._available = self._detect_provider()

    def _detect_provider(self) -> str:
        try:
            import edge_tts
            return "edge"
        except ImportError:
            pass
        try:
            import gtts
            return "gtts"
        except ImportError:
            pass
        return "none"

    def synthesize(self, text: str, output_path: str, **kwargs) -> str:
        clean_text = self._preprocess_text(text)
        provider = self.provider if self.provider != "edge" else self._available

        if provider == "edge":
            return self._edge_synthesize(clean_text, output_path, **kwargs)
        elif provider == "gtts":
            return self._gtts_synthesize(clean_text, output_path, **kwargs)
        else:
            raise RuntimeError("No TTS provider available.")

    def synthesize_sync(self, text: str, output_path: str, **kwargs) -> str:
        return self.synthesize(text, output_path, **kwargs)

    def _edge_synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "zh-CN-YunxiNeural",
        rate: str = "-5%",
        pitch: str = "-3Hz",
    ) -> str:
        import edge_tts

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        async def _do():
            communicate = edge_tts.Communicate(
                text, voice=voice, rate=rate, pitch=pitch
            )
            await communicate.save(str(output_path))

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop — safe to use asyncio.run()
            asyncio.run(_do())
        else:
            # Already inside an event loop — create a new thread to run it
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                fut = pool.submit(asyncio.run, _do())
                fut.result()

        return str(output_path)

    def _gtts_synthesize(self, text: str, output_path: str, lang: str = "zh-CN") -> str:
        from gtts import gTTS

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(str(output_path))
        return str(output_path)

    def _preprocess_text(self, text: str) -> str:
        """Strip script markup so TTS reads only spoken content."""
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Remove all markup lines
            line = re.sub(r'=+\s*$', '', line)
            line = re.sub(r'^#{1,3}\s+', '', line)
            if re.match(r'^\[.*?\]\s*$', line):
                continue
            if re.match(r'^\(.*?\)\s*$', line):
                continue
            line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            line = re.sub(r'^——+——?\s*$', '', line)
            if line:
                lines.append(line)
        result = '。'.join(lines)
        result = re.sub(r'\s+', '', result)
        return result

    def get_available_voices(self) -> list[dict]:
        try:
            import edge_tts
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(edge_tts.list_voices())
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                fut = pool.submit(asyncio.run, edge_tts.list_voices())
                return fut.result()
        except Exception:
            return []
