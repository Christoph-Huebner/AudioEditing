import ffmpeg
import os

class Converter:
    def __init__(self, args):
        # Convert to MP3 parameters
        self.__convert_2_mp3 = getattr(args, 'convert_2_mp3', False)
        self.__bitrate = "320k"
        self.__format = "mp3"
        self.__acodec = "libmp3lame"
        # Dynamic range processing parameters
        self.__dynamic_range_method = getattr(args, 'dynamic_range_method', None)
        self.__threshold = getattr(args, 'threshold', 0)
        self.__ratio = getattr(args, 'ratio', 0)
        self.__attack = getattr(args, 'attack', 0)
        self.__release = getattr(args, 'release', 0)
        # Loudness normalization parameters
        self.__lufs = getattr(args, 'lufs', 0)
        self.__true_peak = getattr(args, 'true_peak', 0)
        self.__loudness_range = getattr(args, 'loudness_range', 0)

    def convert_audio(self, input_file):
        '''
        Applys dynamic range processing and optional converts to MP3.
        '''
        file, ext = os.path.splitext(input_file)
        output_file = f"{file}.mp3" if self.__convert_2_mp3 else input_file

        if (self.__dynamic_range_method is None and (self.__convert_2_mp3 is False or (self.__convert_2_mp3 is True and output_file == input_file))):
            return input_file # No conversion needed, return original file

        if output_file == input_file:
            os.rename(input_file, f"{file}_conv{ext}")
            input_file = f"{file}_conv{ext}"

        try:
            match(self.__dynamic_range_method, self.__convert_2_mp3):
                case "dc", True:
                    (
                        ffmpeg
                        .input(input_file)
                        .filter('acompressor',
                                threshold=self.__threshold + 'dB',
                                ratio=self.__ratio,
                                attack=self.__attack,
                                release=self.__release)
                        .output(output_file, audio_bitrate=self.__bitrate, format=self.__format, acodec=self.__acodec)
                        .run(overwrite_output=True, quiet=True)
                    )
                case "ln", True:
                    (
                        ffmpeg
                        .input(input_file)
                        .output(output_file,
                                af=f"loudnorm=I={self.__lufs}:TP={self.__true_peak}:LRA={self.__loudness_range}:print_format=summary",
                                ar='48k',
                                audio_bitrate=self.__bitrate,
                                format=self.__format,
                                acodec=self.__acodec)
                        .run(overwrite_output=True, quiet=True)
                    )
                case _, True:
                    (
                        ffmpeg
                        .input(input_file)
                        .output(output_file, audio_bitrate=self.__bitrate, format=self.__format, acodec=self.__acodec)
                        .run(overwrite_output=True, quiet=True)
                    )
                case "dc", False:
                    (
                        ffmpeg
                        .input(input_file)
                        .filter('acompressor',
                                threshold=self.__threshold + 'dB',
                                ratio=self.__ratio,
                                attack=self.__attack,
                                release=self.__release)
                        .output(output_file)
                        .run(overwrite_output=True, quiet=True)
                    )
                case "ln", False:
                    (
                        ffmpeg
                        .input(input_file)
                        .output(output_file,
                                af=f"loudnorm=I={self.__lufs}:TP={self.__true_peak}:LRA={self.__loudness_range}:print_format=summary",
                                ar='48k')
                        .run(overwrite_output=True, quiet=True)
                    )
                case _, False:
                    pass # Leave the file unchanged if no conversion is needed, don't remove the original file
            os.remove(input_file)
        except ffmpeg.Error as e:
                print("❌ FFmpeg error:")
                print(e.stderr.decode())
                pass

        return output_file
