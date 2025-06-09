import discord
import logging
from typing import Callable, Dict, List
from .group import FractalGroup

class ZAOFractalVotingView(discord.ui.View):
    """UI view with voting buttons for fractal rounds"""
    
    def __init__(self, fractal_group):
        super().__init__(timeout=None)  # No timeout for persistent buttons
        self.fractal_group = fractal_group
        self.logger = logging.getLogger('bot')
        
        # Create voting buttons
        self.create_voting_buttons()
    
    def create_voting_buttons(self):
        """Create a button for each active candidate"""
        # Clear any existing buttons
        self.clear_items()
        
        # List of button styles to cycle through
        styles = [
            discord.ButtonStyle.primary,    # Blue
            discord.ButtonStyle.success,    # Green
            discord.ButtonStyle.danger,     # Red 
            discord.ButtonStyle.secondary   # Grey
        ]
        
        # Create a button for each candidate
        for i, candidate in enumerate(self.fractal_group.active_candidates):
            # Cycle through button styles
            style = styles[i % len(styles)]
            
            # Create button with candidate name
            button = discord.ui.Button(
                style=style,
                label=candidate.display_name,
                custom_id=f"vote_{candidate.id}"
            )
            
            # Create and assign callback
            button.callback = self.create_vote_callback(candidate)
            self.add_item(button)
            
        self.logger.info(f"Created {len(self.fractal_group.active_candidates)} voting buttons")
    
    def create_vote_callback(self, candidate):
        """Create a callback function for voting buttons"""
        async def vote_callback(interaction):
            # Always defer response immediately to avoid timeout
            await interaction.response.defer(ephemeral=True)
            
            try:
                # Process the vote (public announcement happens in process_vote)
                await self.fractal_group.process_vote(interaction.user, candidate)
                
                # Confirm to the voter (private)
                await interaction.followup.send(
                    f"You voted for {candidate.display_name}",
                    ephemeral=True
                )
                
            except Exception as e:
                self.logger.error(f"Error processing vote: {e}", exc_info=True)
                await interaction.followup.send(
                    "❌ Error recording your vote. Please try again.",
                    ephemeral=True
                )
                
        return vote_callback


class FractalGroupModal(discord.ui.Modal):
    """Modal for creating a new fractal group"""
    
    def __init__(self, cog):
        super().__init__(title="Create ZAO Fractal Group")
        self.cog = cog
        self.logger = logging.getLogger('bot')
        
        # Text input for group name
        self.group_name = discord.ui.TextInput(
            label="Group Name",
            placeholder="Enter a name for this fractal group",
            min_length=3,
            max_length=50,
            required=True
        )
        self.add_item(self.group_name)
    
    async def on_submit(self, interaction):
        """Handle modal submission to create a new fractal group"""
        # Defer response to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        try:
            self.logger.info(f"Creating fractal group '{self.group_name.value}' for {interaction.user.display_name}")
            
            # Create private thread for the group
            thread = await interaction.channel.create_thread(
                name=f"ZAO Fractal: {self.group_name.value}",
                type=discord.ChannelType.private_thread,
                reason=f"ZAO Fractal Group created by {interaction.user.display_name}"
            )
            
            # Initialize group
            group = FractalGroup(thread, interaction.user)
            
            # Store group in cog's active groups
            self.cog.active_groups[thread.id] = group
            
            # Add members from voice channel to the group and thread
            voice_check = await self.cog.check_voice_state(interaction.user)
            if voice_check['success']:
                for member in voice_check['members']:
                    await group.add_member(member)
            
            # Start first round
            await group.start_new_round()
            
            # Notify success
            await interaction.followup.send(
                f"✅ ZAO Fractal Group '{self.group_name.value}' created in thread {thread.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            self.logger.error(f"Error in modal submission: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error creating fractal group: {str(e)}",
                ephemeral=True
            )
