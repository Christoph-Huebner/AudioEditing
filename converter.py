import ffmpeg
import os

class Converter:
    def __init__(self, args):
        # Convert to MP3 parameters
        self.__convert_2_mp3 = args.convert_2_mp3
        self.__bitrate = "320k"
        self.__format = "mp3"
        self.__acodec = "libmp3lame"
        # Dynamic range processing parameters
        self.__dynamic_range_method = args.dynamic_range_method
        self.__threshold = args.threshold
        self.__ratio = args.ratio
        self.__attack = args.attack
        self.__release = args.release
        # Loudness normalization parameters
        self.__lufs = args.lufs
        self.__true_peak = args.true_peak
        self.__loudness_range = args.loudness_range

    def convert_audio(self, input_file):
        '''
        Applys dynamic range processing and optional converts to MP3.
        '''
        output_file, ext = os.path.splitext(input_file)
        if self.__convert_2_mp3:
            output_file = output_file + ".mp3"
        else:
            output_file = output_file + ext

        if self.__convert_2_mp3 and ext.lower() == '.mp3':
            return input_file  # No conversion needed if already in MP3 format

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
                    pass # No processing needed if no dynamic range method is specified. It's fine that this is handled here.
        except ffmpeg.Error as e:
                print("❌ FFmpeg error:")
                print(e.stderr.decode())
                pass

        return output_file
