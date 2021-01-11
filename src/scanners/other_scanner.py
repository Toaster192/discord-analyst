from typing import List, Dict
import discord


# Custom libs

from .scanner import Scanner
from . import EmotesScanner
from data_types import Other, Emote, get_emote_dict
from logs import ChannelLogs, MessageLog


class OtherScanner(Scanner):
    @staticmethod
    def help() -> str:
        return "```\n"
        +"%other : Show other statistics\n"
        +"arguments:\n"
        +"* @member : filter for one or more member\n"
        +"* #channel : filter for one or more channel\n"
        +"Example: %other #mychannel1 @user\n"
        +"```"

    def __init__(self):
        super().__init__(
            help=OtherScanner.help(),
            intro_context="Other data",
        )

    async def init(self, message: discord.Message, *args: str) -> bool:
        self.other = Other()
        # Create emotes dict from custom emojis of the guild
        self.emotes = get_emote_dict(message.channel.guild)
        return True

    def compute_message(self, channel: ChannelLogs, message: MessageLog):
        EmotesScanner.analyse_message(
            message, self.emotes, self.raw_members, all_emojis=True
        )
        return OtherScanner.analyse_message(
            channel, message, self.other, self.raw_members
        )

    def get_results(self, intro: str) -> List[str]:
        OtherScanner.compute_results(self.other, self.emotes)
        res = [intro]
        res += self.other.to_string(
            show_top_channel=len(self.channels) > 1,
            show_mentioned=(len(self.members) > 0),
        )
        return res

    @staticmethod
    def analyse_message(
        channel: ChannelLogs, message: MessageLog, other: Other, raw_members: List[int]
    ) -> bool:
        impacted = False
        # If author is included in the selection (empty list is all)
        if not message.bot and (len(raw_members) == 0 or message.author in raw_members):
            impacted = True
            other.channel_usage[channel.id] += 1
        for mention in message.mentions:
            if mention in raw_members:
                other.mentions[mention] += 1
        return impacted

    @staticmethod
    def compute_results(other: Other, emotes: Dict[str, Emote]):
        # calculate most used reaction
        other.most_used_reaction = sorted(emotes, key=lambda k: emotes[k].reactions)[-1]
        other.most_used_reaction_count = emotes[other.most_used_reaction].reactions
        # calculate total reactions
        other.used_reaction_total = sum([emote.reactions for emote in emotes.values()])
