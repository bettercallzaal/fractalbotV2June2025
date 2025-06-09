import discord
import logging
import asyncio
from typing import Optional, List, Dict

class FractalGroup:
    """Core class for managing a fractal voting group"""
    
    def __init__(self, thread: discord.Thread, facilitator: discord.Member):
        """Initialize a new fractal group"""
        self.thread = thread
        self.facilitator = facilitator
        self.members = []
        self.active_candidates = []  # Members currently in voting pool
        self.votes = {}  # Dict mapping voter_id to candidate_id
        self.winners = {}  # Dict mapping level to winner
        self.current_level = 6  # Start at level 6
        self.current_voting_message = None
        self.logger = logging.getLogger('bot')
        
        self.logger.info(f"Created fractal group '{thread.name}' with facilitator {facilitator.display_name}")
        
    async def add_member(self, member: discord.Member):
        """Add a member to the fractal group"""
        if member not in self.members:
            self.members.append(member)
            self.active_candidates.append(member)
            await self.thread.add_user(member)
            self.logger.info(f"Added {member.display_name} to fractal group '{self.thread.name}'")

    async def start_new_round(self, winner: Optional[discord.Member] = None):
        """Start a new voting round, optionally recording a previous winner"""
        # Process previous winner if exists
        if winner:
            self.winners[self.current_level] = winner
            self.active_candidates.remove(winner)  # Remove from active candidates
            self.current_level -= 1  # Move to next level
            
            # Send prominent winner announcement
            await self.thread.send(
                f"# 🎉 LEVEL {self.current_level + 1} WINNER: {winner.mention}! 🎉\n\n"
                f"Moving to Level {self.current_level}..."
            )
        
        # Check if we've reached the end
        if self.current_level < 1 or len(self.active_candidates) <= 1:
            await self.end_fractal()
            return
            
        # Reset votes for new round
        self.votes = {}
        
        # Log active candidates
        candidate_names = ", ".join([c.display_name for c in self.active_candidates])
        self.logger.info(f"Starting level {self.current_level} with {len(self.active_candidates)} candidates: {candidate_names}")
        
        try:
            # Import here to avoid circular import
            from .views import ZAOFractalVotingView
            
            # Create voting view with buttons
            view = ZAOFractalVotingView(self)
            
            # Show voting instructions
            votes_needed = self.get_vote_threshold()
            message = await self.thread.send(
                f"## 🗳️ Voting for Level {self.current_level}\n\n"
                f"**Candidates:** {', '.join([c.mention for c in self.active_candidates])}\n"
                f"**Votes Needed to Win:** {votes_needed} ({votes_needed}/{len(self.members)} members)\n\n"
                f"Click a button below to vote. Your vote will be announced publicly.\n"
                f"You can change your vote at any time by clicking a different button.",
                view=view
            )
            self.current_voting_message = message
            
        except Exception as e:
            self.logger.error(f"Error creating voting UI: {e}", exc_info=True)
            await self.thread.send("❌ Error setting up voting buttons. Please try again.")

    def get_vote_threshold(self):
        """Calculate votes needed to win (50% or more)"""
        return max(1, len(self.members) // 2 + len(self.members) % 2)  # Ceiling division

    async def process_vote(self, voter: discord.Member, candidate: discord.Member):
        """Process a vote and announce it publicly"""
        previous_vote = self.votes.get(voter.id)
        previous_candidate = None
        
        if previous_vote:
            previous_candidate = discord.utils.get(self.active_candidates + [m for m in self.members if m.id in [w.id for w in self.winners.values()]], id=previous_vote)
        
        # Update vote
        self.votes[voter.id] = candidate.id
        
        # Announce vote publicly
        if previous_candidate:
            await self.thread.send(
                f"🔄 **Vote Changed:** {voter.mention} changed vote from {previous_candidate.mention} to {candidate.mention}"
            )
        else:
            await self.thread.send(
                f"✅ **New Vote:** {voter.mention} voted for {candidate.mention}"
            )
        
        # Check if this vote caused a winner
        await self.check_for_winner()

    async def check_for_winner(self):
        """Check if any candidate has reached the vote threshold"""
        vote_counts = {}
        
        # Count votes for each candidate
        for candidate_id in self.votes.values():
            vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1
        
        threshold = self.get_vote_threshold()
        
        # Check for a winner
        for candidate_id, count in vote_counts.items():
            if count >= threshold:
                winner = discord.utils.get(self.active_candidates, id=candidate_id)
                if winner:
                    # Log winner info
                    self.logger.info(f"Winner for level {self.current_level}: {winner.display_name} with {count}/{len(self.members)} votes")
                    await self.start_new_round(winner)
                    return

    async def end_fractal(self):
        """End the fractal process and show final results"""
        result_message = "# 🏆 ZAO Fractal Results 🏆\n\n"
        
        # Show winners for each level
        for level in range(6, 0, -1):
            winner = self.winners.get(level)
            if winner:
                result_message += f"**Level {level}**: {winner.mention}\n"
                
        # Handle any remaining member if only one left
        if len(self.active_candidates) == 1:
            last_member = self.active_candidates[0]
            self.winners[self.current_level] = last_member
            result_message += f"**Level {self.current_level}**: {last_member.mention} (default winner)\n"
        
        await self.thread.send(result_message)
        await self.thread.send("### 🎊 This fractal group is now complete! Thank you all for participating.")
        self.logger.info(f"Fractal group '{self.thread.name}' completed successfully")
