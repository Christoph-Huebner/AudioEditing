import ffmpeg
import os

FORMAT_OPTIONS = {
    # MP3 (MPEG-1/2 Audio Layer III)
    # Very compatible, especially useful for older devices, car radios and USB playback.
    # Typical bitrates: 128k (medium), 192k (good), 256k (high), 320k (maximum CBR).
    "mp3": {
        "format": "mp3",
        "acodec": "libmp3lame",
        "audio_bitrate": "256k",
    },

    # M4A (AAC audio in MPEG-4 container)
    # Recommended modern format for a good balance between quality and file size.
    # FFmpeg uses the MP4 muxer for .m4a files.
    # Typical bitrates: 128k, 192k, 256k.
    "m4a": {
        "format": "mp4",
        "acodec": "aac",
        "audio_bitrate": "192k",
    },

    # FLAC (Free Lossless Audio Codec)
    # Lossless format. Useful for archival/intermediate files, but it does not improve
    # already compressed sources such as YouTube audio.
    # No bitrate is needed. Compression level 6 is a common trade-off.
    "flac": {
        "format": "flac",
        "acodec": "flac",
        "compression_level": 6,
    },

    # WAV (uncompressed PCM audio)
    # Very large files. Useful as an intermediate/editing format.
    # 16-bit PCM is widely compatible and sufficient for compressed input sources.
    "wav": {
        "format": "wav",
        "acodec": "pcm_s16le",
    },

    # Opus
    # Very efficient modern codec. Good for small files and speech/music,
    # but less universally supported than MP3 or M4A on older devices.
    "opus": {
        "format": "opus",
        "acodec": "libopus",
        "audio_bitrate": "128k",
    },
}

class Converter:
    def __init__(self, args):
        # Conversion parameters
        self.__convert_2_mp3 = getattr(args, "convert_2_mp3", False)

        # Dynamic range processing parameters
        self.__dynamic_range_method = getattr(args, "dynamic_range_method", None)

        # Defaults for dynamic compression.
        # These are moderate starting values and much safer than 0.
        self.__threshold = getattr(args, "threshold", None) or -18
        self.__ratio = getattr(args, "ratio", None) or 2
        self.__attack = getattr(args, "attack", None) or 20
        self.__release = getattr(args, "release", None) or 250

        # Defaults for loudness normalization.
        # -16 LUFS is a practical default for local playback/music collections.
        # TP=-1.5 helps avoid clipping; LRA=11 is a moderate range target.
        self.__lufs = getattr(args, "lufs", None) or -16
        self.__true_peak = getattr(args, "true_peak", None) or -1.5
        self.__loudness_range = getattr(args, "loudness_range", None) or 11

    def convert_audio(self, input_file):
        """
        Applies dynamic range processing and optionally converts the file to MP3.
        """
        file_base, source_ext = os.path.splitext(input_file)

        source_format = source_ext.lstrip(".").lower()
        target_format = "mp3" if self.__convert_2_mp3 else source_format

        final_output_file = f"{file_base}.{target_format}"

        # Check if valid dynamic range method is set, e.g. not nl instead of ln
        valid_methods = {None, "dc", "ln"}
        if self.__dynamic_range_method not in valid_methods:
            print(f"❌ Unsupported dynamic range method: {self.__dynamic_range_method}")
            return input_file

        # Nothing to do:
        # - no dynamic range processing selected
        # - no format conversion requested
        if self.__dynamic_range_method is None and final_output_file == input_file:
            return input_file

        opts = FORMAT_OPTIONS.get(target_format)

        if opts is None:
            print(f"❌ Unsupported target format: {target_format}")
            return input_file

        # FFmpeg cannot safely read from and write to the same file.
        # Therefore we always write to a temporary output file first and replace
        # the final file only after a successful conversion.
        temp_output_file = f"{file_base}.converted.{target_format}"

        try:
            stream = ffmpeg.input(input_file)

            if self.__dynamic_range_method == "dc":
                stream = stream.filter(
                    "acompressor",
                    threshold=f"{self.__threshold}dB",
                    ratio=self.__ratio,
                    attack=self.__attack,
                    release=self.__release,
                )

                stream.output(
                    temp_output_file,
                    **opts,
                ).run(
                    overwrite_output=True,
                    capture_stdout=True,
                    capture_stderr=True,
                )

            elif self.__dynamic_range_method == "ln":
                loudnorm_filter = (
                    f"loudnorm=I={self.__lufs}:"
                    f"TP={self.__true_peak}:"
                    f"LRA={self.__loudness_range}:"
                    f"print_format=summary"
                )

                stream.output(
                    temp_output_file,
                    af=loudnorm_filter,
                    ar="48000",
                    **opts,
                ).run(
                    overwrite_output=True,
                    capture_stdout=True,
                    capture_stderr=True,
                )

            else:
                stream.output(
                    temp_output_file,
                    **opts,
                ).run(
                    overwrite_output=True,
                    capture_stdout=True,
                    capture_stderr=True,
                )

            # Replace the final output only after FFmpeg has completed successfully.
            os.replace(temp_output_file, final_output_file)

            # Remove the original input file only if the output is a different file.
            if os.path.abspath(input_file) != os.path.abspath(final_output_file):
                os.remove(input_file)

            return final_output_file

        except ffmpeg.Error as e:
            print("❌ FFmpeg error:")
            stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
            print(stderr)

            if os.path.exists(temp_output_file):
                os.remove(temp_output_file)

            return input_file

        except Exception as e:
            print(f"❌ Unexpected error: {e}")

            if os.path.exists(temp_output_file):
                os.remove(temp_output_file)

            return input_file
