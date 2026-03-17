# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""STT（语音转文字）扩展接口

当前环境未配置STT引擎，提供基类和预留实现。
安装STT引擎后，通过 generate_minutes(audio_path=..., stt_engine=...) 调用。
"""


class BaseSTTEngine:
    """STT引擎基类，所有实现必须继承此接口"""

    def transcribe(self, audio_path: str) -> str:
        """将音频文件转写为文本

        Args:
            audio_path: 音频文件路径（支持 wav/mp3/ogg/m4a/flac）

        Returns:
            转写后的纯文本

        Raises:
            NotImplementedError: 子类必须实现
            FileNotFoundError: 音频文件不存在
            RuntimeError: 转写失败
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """引擎名称"""
        return self.__class__.__name__

    @property
    def supported_formats(self) -> list:
        """支持的音频格式"""
        return [".wav", ".mp3", ".ogg", ".m4a", ".flac", ".silk"]


class WhisperLocalSTT(BaseSTTEngine):
    """本地Whisper引擎（需安装 openai-whisper）

    安装: pip install openai-whisper
    """

    def transcribe(self, audio_path: str) -> str:
        try:
            import whisper
        except ImportError:
            raise RuntimeError(
                "openai-whisper 未安装。请运行: pip install openai-whisper"
            )
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, language="zh")
        return result["text"].strip()


class SenseVoiceSTT(BaseSTTEngine):
    """硅基流动 SenseVoice API 引擎

    需要配置环境变量:
    - SENSEVOICE_API_URL: API地址
    - SENSEVOICE_API_KEY: API密钥
    """

    def transcribe(self, audio_path: str) -> str:
        import os
        api_url = os.environ.get("SENSEVOICE_API_URL")
        api_key = os.environ.get("SENSEVOICE_API_KEY")
        if not api_url or not api_key:
            raise RuntimeError(
                "SenseVoice API 未配置。请设置 SENSEVOICE_API_URL 和 SENSEVOICE_API_KEY"
            )
        import requests
        with open(audio_path, "rb") as f:
            resp = requests.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": f},
                timeout=300,
            )
        resp.raise_for_status()
        data = resp.json()
        return data.get("text", "").strip()


class OpenAIWhisperSTT(BaseSTTEngine):
    """OpenAI Whisper API 引擎

    需要配置环境变量:
    - OPENAI_API_KEY: OpenAI API密钥
    """

    def transcribe(self, audio_path: str) -> str:
        import os
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY 未配置")

        with open(audio_path, "rb") as f:
            import requests
            resp = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": (os.path.basename(audio_path), f)},
                data={"model": "whisper-1", "language": "zh"},
                timeout=300,
            )
        resp.raise_for_status()
        data = resp.json()
        return data.get("text", "").strip()


def get_available_engine() -> BaseSTTEngine:
    """自动检测可用的STT引擎

    优先级: WhisperLocal > OpenAIWhisper > SenseVoice > None

    Returns:
        可用的STT引擎实例，或None
    """
    # 检查本地Whisper
    try:
        import whisper  # noqa: F401
        return WhisperLocalSTT()
    except ImportError:
        pass

    # 检查OpenAI API
    import os
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIWhisperSTT()

    # 检查SenseVoice API
    if os.environ.get("SENSEVOICE_API_KEY"):
        return SenseVoiceSTT()

    return None
