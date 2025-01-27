from application.strategy import STTStrategy
from domain.value_object import YouTubeScript, YouTubeScriptChunk

from youtube_transcript_api import YouTubeTranscriptApi


class AutoYoutubeStrategy(STTStrategy):
    def transcribe(self, video_id: str) -> str:
        try:
            result = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en', 'en-GB'])
            return result

        except Exception as e:
            print(e)
            return None

    def transcribe_to_script(self, audio_link: str) -> YouTubeScript:
        result = self.transcribe(audio_link)
        if result is None:
            return None

        youtube_script = YouTubeScript(
            script=' '.join(chunk['text'] for chunk in result if chunk['text'] != '[음악]'),
            chunks=[
                YouTubeScriptChunk.from_dict({'timestamp': (float(chunk['start']), float(chunk['start']) + float(chunk['duration'])), 'text': chunk['text']})
                for chunk in result if chunk['text'] != '[음악]'
            ],
        )
        return youtube_script
