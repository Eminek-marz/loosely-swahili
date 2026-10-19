"""
Anjiru.AI Audio Beat Synthesizer & Songwriter Studio
Procedural audio synthesis (WAV) and multi-register lyric composition (Sheng, Swahili, English).
"""

import math
import numpy as np
import wave
import struct
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = PROJECT_ROOT / "workspace" / "projects" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


class AnjiruAudioSynthesizer:
    """Procedural WAV audio synthesizer generating authentic rhythm sections."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def _create_kick(self, duration: float = 0.45, start_freq: float = 145.0, end_freq: float = 38.0) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Exponential frequency drop
        freq_envelope = end_freq + (start_freq - end_freq) * np.exp(-t * 22.0)
        phase = 2.0 * np.pi * np.cumsum(freq_envelope) / self.sample_rate
        # Amplitude envelope: quick attack, punchy exponential release
        amp_envelope = np.exp(-t * 7.5)
        # Add subtle warm saturation
        raw_kick = np.sin(phase) * amp_envelope
        saturated = np.tanh(raw_kick * 1.6)
        return saturated

    def _create_snare(self, duration: float = 0.3) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Tonal body
        body = np.sin(2.0 * np.pi * 185.0 * t) * np.exp(-t * 24.0)
        # Noise burst (white noise bandpass approximation)
        noise = (np.random.uniform(-1.0, 1.0, len(t))) * np.exp(-t * 16.0)
        snare = (body * 0.45 + noise * 0.55)
        return np.tanh(snare * 1.3)

    def _create_hihat(self, duration: float = 0.08, open_hat: bool = False) -> np.ndarray:
        if open_hat:
            duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Metallic multi-oscillator frequency modulation + high noise
        metallic = (
            np.sin(2 * np.pi * 3200 * t) +
            np.sin(2 * np.pi * 4800 * t) +
            np.sin(2 * np.pi * 7100 * t) +
            np.random.uniform(-0.8, 0.8, len(t))
        )
        decay_rate = 8.0 if open_hat else 45.0
        envelope = np.exp(-t * decay_rate)
        return (metallic * 0.25 * envelope)

    def _create_808_bass(self, freq: float, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        # Sub sine with slight second harmonic for mobile speaker presence
        sub = np.sin(2 * np.pi * freq * t)
        harmonic = 0.25 * np.sin(2 * np.pi * freq * 2.0 * t)
        envelope = np.clip(1.0 - (t / duration) * 0.4, 0, 1.0)
        return np.tanh((sub + harmonic) * 1.4) * envelope * 0.85

    def _mix_tracks(self, length_samples: int, events: List[Dict[str, Any]]) -> np.ndarray:
        master = np.zeros(length_samples, dtype=np.float32)
        for ev in events:
            sample = ev["sample"]
            start_idx = int(ev["time_sec"] * self.sample_rate)
            gain = ev.get("gain", 1.0)
            end_idx = min(length_samples, start_idx + len(sample))
            if start_idx < length_samples:
                master[start_idx:end_idx] += sample[:end_idx - start_idx] * gain
        # Soft-clip master limiter
        master = np.tanh(master * 0.95)
        return master

    def synthesize_beat(self, style: str = "gengetone", bars: int = 4, bpm: Optional[int] = None) -> Dict[str, Any]:
        """
        Synthesize full rhythm beat according to requested musical style:
        - gengetone: 104 BPM, Kenyan Dembow 3-3-2 rhythm, booming sub kick & syncopated snare.
        - afrobeats: 108 BPM, syncopated log-drum, polyrhythmic rimshots & shakers.
        - trap: 140 BPM, rolling 808 sub, hi-hat triplets & sharp snares.
        - lofi: 84 BPM, laid back jazzy drums with warm bass.
        """
        style = style.lower()
        if style == "gengetone":
            tempo = bpm or 104
        elif style == "afrobeats":
            tempo = bpm or 108
        elif style == "trap":
            tempo = bpm or 140
        else:
            style = "lofi"
            tempo = bpm or 84

        beat_sec = 60.0 / tempo
        bar_sec = beat_sec * 4.0
        total_duration = bar_sec * bars
        total_samples = int(total_duration * self.sample_rate)

        kick = self._create_kick()
        snare = self._create_snare()
        hat_closed = self._create_hihat(open_hat=False)
        hat_open = self._create_hihat(open_hat=True)

        events: List[Dict[str, Any]] = []

        # Bass notes frequencies (Root, 4th, 5th, Minor 6th)
        bass_notes = [43.65, 43.65, 51.91, 48.99]  # F, F, G#, G

        for bar in range(bars):
            bar_start = bar * bar_sec
            bass_freq = bass_notes[bar % len(bass_notes)]

            # 808 Bassline
            events.append({
                "sample": self._create_808_bass(bass_freq, bar_sec * 0.9),
                "time_sec": bar_start + 0.01,
                "gain": 0.9
            })

            if style == "gengetone":
                # Dembow 3-3-2 syncopation
                # Kick on beat 1 and beat 3
                events.append({"sample": kick, "time_sec": bar_start, "gain": 1.0})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 2.0, "gain": 0.95})

                # Syncopated Dembow snares on 1.75 and 3.5
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 0.75, "gain": 0.85})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 1.5, "gain": 0.9})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 2.75, "gain": 0.85})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 3.5, "gain": 0.95})

                # 1/8 note hi-hats
                for step in range(8):
                    t_hat = bar_start + step * (beat_sec / 2.0)
                    events.append({"sample": hat_closed, "time_sec": t_hat, "gain": 0.45})

            elif style == "afrobeats":
                # Kick pattern
                events.append({"sample": kick, "time_sec": bar_start, "gain": 1.0})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 1.5, "gain": 0.75})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 2.0, "gain": 0.9})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 3.25, "gain": 0.8})

                # Rimshot snares
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 1.0, "gain": 0.85})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 2.75, "gain": 0.9})

                # Polyrhythmic shakers / hats
                for step in range(16):
                    t_hat = bar_start + step * (beat_sec / 4.0)
                    gain = 0.55 if step % 2 == 0 else 0.35
                    events.append({"sample": hat_closed, "time_sec": t_hat, "gain": gain})

            elif style == "trap":
                # Trap kick on 1 and off-beats
                events.append({"sample": kick, "time_sec": bar_start, "gain": 1.0})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 2.25, "gain": 0.85})
                if bar % 2 == 1:
                    events.append({"sample": kick, "time_sec": bar_start + beat_sec * 3.5, "gain": 0.9})

                # Snare on 3
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 2.0, "gain": 1.0})

                # Fast rolling hats
                for step in range(16):
                    t_hat = bar_start + step * (beat_sec / 4.0)
                    is_triplet = (bar == bars - 1 and step >= 12)
                    events.append({"sample": hat_closed, "time_sec": t_hat, "gain": 0.5})

            else:  # lofi
                events.append({"sample": kick, "time_sec": bar_start, "gain": 0.9})
                events.append({"sample": kick, "time_sec": bar_start + beat_sec * 2.5, "gain": 0.75})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 1.0, "gain": 0.8})
                events.append({"sample": snare, "time_sec": bar_start + beat_sec * 3.0, "gain": 0.85})
                for step in range(8):
                    t_hat = bar_start + step * (beat_sec / 2.0)
                    events.append({"sample": hat_closed, "time_sec": t_hat, "gain": 0.35})

        master_audio = self._mix_tracks(total_samples, events)
        int16_audio = (master_audio * 32767).astype(np.int16)

        filename = f"anjiru_{style}_{tempo}bpm_{bars}bars.wav"
        file_path = AUDIO_DIR / filename

        with wave.open(str(file_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(int16_audio.tobytes())

        return {
            "status": "success",
            "style": style,
            "tempo_bpm": tempo,
            "bars": bars,
            "duration_sec": round(total_duration, 2),
            "file_name": filename,
            "file_path": str(file_path),
            "url": f"/api/audio/download?file={filename}",
            "size_bytes": os.path.getsize(str(file_path))
        }


class AnjiruSongwriter:
    """Songwriter creating structured lyrics, flow cadences, and chord progressions."""

    def compose_song(self, theme: str, style: str = "gengetone", language: str = "sheng") -> Dict[str, Any]:
        synth = AnjiruAudioSynthesizer()
        beat_info = synth.synthesize_beat(style=style, bars=8)

        # Build theme-focused lyrical structure
        theme_clean = theme.strip().title() if theme else "Nairobi Cyberpunk"

        if language in ["sheng", "loosely_swahili"]:
            title = f"Rada ya {theme_clean} (Anjiru Anthem)"
            key_sig = "F Minor"
            chords = "Fm — Db — Ab — Eb"
            lyrics = {
                "intro": f"""(Yeah! Anjiru Studio on the beat! Kanairo city lights, 254 code execution...)
Yo, cheki hii script inavyo-run bila bug,
Microphone test, one-two, token economy full stack!""",
                "verse_1": f"""Nilitoka kitaa nikiwa na ndoto na laptop moja tu,
Nilipiga ma-code za usiku bila ku-complain wala issue.
Sasa algorithms zetu zina-conquer Nairobi mzima,
Kuanzia Eastlands hadi Westlands ma-server zina-simama.
Database ina-stream, zero latency kwa ground,
Hakuna ku-lag, hii ni sovereign intelligence sound!""",
                "pre_chorus": f"""Mapema ndio best, weka logic kwa lane,
Compile hii vision, hakuna tena pain.
Waliosema hatuwezi sasa wana-take notes,
Anjiru neural engine ina-vuka ma-boats!""",
                "chorus": f"""{theme_clean.upper()}! Ni ya kwetu, hatubahatishi!
Ma-bytes zina-flow, akili safi hatu-glitch!
Kila mistari ni code, kila beat ni revolution,
Anjiru intelligence, the sovereign Kenyan solution! (REPEAT 2X)""",
                "verse_2": f"""Neural weights ziko tuned, 72 percent token save,
Bantu morphotactics zina-ride hii sound wave.
Kutoka River Road ma-hustler wana-push tech kwa cloud,
Hatuombi ruhusa, we make our ancestors proud.
Binary rhythm inalia, CPU iko 100 percent,
Hii sio demo tu, hii ni historical event!""",
                "bridge": f"""(Bassline drop — 808 sub kick glide)
Sheng ina-speak, Python ina-compile,
East Africa stand up, we do this with style!""",
                "outro": f"""Anjiru.AI Audio Studio.
Produced with procedural audio synthesis.
Nairobi, Kenya to the World. Peace!"""
            }
        elif language == "swahili":
            title = f"Utenzi wa {theme_clean} (Muziki Sanifu)"
            key_sig = "D Minor"
            chords = "Dm — Bb — F — C"
            lyrics = {
                "intro": f"""(Mlio wa ngoma za asili na ala za kielektroniki...)
Sikilizeni wito, kutoka tambarare za Afrika Mashariki,
Akili bandia ya asili inapoamka kwa hekima na uthabiti.""",
                "verse_1": f"""Tulianza safari gizani, tukiwa na kalamu na ndoto,
Maneno ya Kiswahili yakichanua kama mwanga wa moto.
Sayansi ya mahesabu sasa inatamka lugha yetu,
Hatuko nyuma tena, huu ni urithi wa taifa letu.""",
                "pre_chorus": f"""Tazama mifumo inavyofunguka kwa uzuri,
Kila baiti na neno lina maana na shauri.""",
                "chorus": f"""{theme_clean.upper()}! Mwanga wa hekima zetu,
Huu ni wimbo wa ustawi, fahari ya bara letu!
Kutoka pwani hadi milimani sauti inavuma,
Akili ya asili ya Anjiru inasimama daima!""",
                "verse_2": f"""Hekima za kale zimeunganishwa na sayansi ya kisasa,
Hakuna tena vizuizi, tunaondoa kila shaka na giza.
Tunalinda uhuru wetu wa kidijitali na maarifa,
Kwa ujasiri na umoja, tunajenga heshima ya taifa.""",
                "bridge": f"""(Ala ya kinanda inapanda juu...)
Lugha yetu ni utambulisho,
Sayansi yetu ni ushindi!""",
                "outro": f"""Imetungwa na Anjiru.AI.
Utafiti na Muziki wa Asili.
Kenya Inasonga Mbele."""
            }
        else:  # English
            title = f"Sovereign Mind: {theme_clean} (Electronic Anthem)"
            key_sig = "C Minor"
            chords = "Cm — Ab — Eb — Bb"
            lyrics = {
                "intro": f"""(System boot chime... 808 sub harmonic pulse begins)
Initializing neural audio pipeline...
Zero dropped frames, infinite algorithmic bandwidth.""",
                "verse_1": f"""Started in the terminal, lines of code upon the screen,
Synthesizing structures that the world had never seen.
Breaking through the latency, rewriting every rule,
From the heart of Nairobi, computational fuel.
Distributed intelligence, high-density precision,
Turning raw equations into sovereign decision.""",
                "pre_chorus": f"""Elevate the clock speed, watch the matrices align,
We wrote the future into memory by design.""",
                "chorus": f"""{theme_clean.upper()}! Sovereign from the core,
This is the threshold that unlocks the open door!
No limitations, no boundaries in sight,
Anjiru intelligence blazing through the night! (REPEAT 2X)""",
                "verse_2": f"""72 percent compression on the tokenized stream,
Manifesting reality beyond a simple dream.
Sub-bass oscillating through the architecture base,
Building new horizons in continuous vector space.
Hardware synchronized, parallel threads alive,
This is how sovereign foundations survive!""",
                "bridge": f"""(Full frequency drop — filter sweep)
Logic meets art. Code meets frequency.
The indigenous foundation has arrived.""",
                "outro": f"""Anjiru.AI Audio Studio.
Synthesized via procedural waveforms.
End of transmission."""
            }

        return {
            "status": "success",
            "title": title,
            "theme": theme_clean,
            "style": style,
            "language": language,
            "tempo_bpm": beat_info["tempo_bpm"],
            "key_signature": key_sig,
            "chord_progression": chords,
            "lyrics": lyrics,
            "audio": beat_info
        }


# Global singleton
_audio_synth = None
_songwriter = None

def get_audio_synth() -> AnjiruAudioSynthesizer:
    global _audio_synth
    if _audio_synth is None:
        _audio_synth = AnjiruAudioSynthesizer()
    return _audio_synth

def get_songwriter() -> AnjiruSongwriter:
    global _songwriter
    if _songwriter is None:
        _songwriter = AnjiruSongwriter()
    return _songwriter
