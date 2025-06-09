import discord
from discord import app_commands
from discord.ext import commands
import logging
from ..base import BaseCog
from .views import FractalGroupModal
from .group import FractalGroup

class FractalCog(BaseCog):
    """Cog for handling ZAO Fractal voting commands and logic"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.logger = logging.getLogger('bot')
        self.active_groups = {}  # Dict mapping thread_id to FractalGroup
    
    @app_commands.command(
        name="zaofractal",
        description="Create a new ZAO fractal voting group from your current voice channel"
    )
    async def zaofractal(self, interaction: discord.Interaction):
        """Create a new ZAO fractal voting group from voice channel members"""
        # Always defer first to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check user's voice state
            voice_check = await self.check_voice_state(interaction.user)
            
            if not voice_check['success']:
                await interaction.followup.send(voice_check['message'], ephemeral=True)
                return
            
            # Open group creation modal
            modal = FractalGroupModal(self)
            await interaction.followup.send(
                "⚙️ Creating your ZAO Fractal group...",
                ephemeral=True
            )
            await interaction.edit_original_response(
                content="✅ Please fill out the group information:",
                view=discord.ui.View().add_item(
                    discord.ui.Button(
                        label="Create ZAO Fractal Group",
                        style=discord.ButtonStyle.primary,
                        custom_id="create_fractal_group"
                    )
                )
            )
            
            # Show modal when button is clicked
            @discord.ui.button(
                label="Create ZAO Fractal Group",
                style=discord.ButtonStyle.primary,
                custom_id="create_fractal_group"
            )
            async def button_callback(button_interaction):
                await button_interaction.response.send_modal(modal)
            
        except Exception as e:
            self.logger.error(f"Error creating fractal group: {e}", exc_info=True)
            await interaction.followup.send(
                f"❌ Error creating fractal group: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="endgroup",
        description="End an active fractal group (facilitator only)"
    )
    async def end_group(self, interaction: discord.Interaction):
        """End an active fractal group"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if in a fractal thread
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("❌ This command can only be used in a fractal group thread.", ephemeral=True)
            return
        
        # Check if this is an active fractal group
        group = self.active_groups.get(interaction.channel.id)
        if not group:
            await interaction.followup.send("❌ This thread is not an active fractal group.", ephemeral=True)
            return
        
        # Check if user is facilitator
        if interaction.user.id != group.facilitator.id:
            await interaction.followup.send("❌ Only the group facilitator can end the fractal group.", ephemeral=True)
            return
        
        # End the fractal group
        await group.end_fractal()
        del self.active_groups[interaction.channel.id]
        
        await interaction.followup.send("✅ Fractal group ended successfully.", ephemeral=True)
    
    @app_commands.command(
        name="status",
        description="Show the current status of an active fractal group"
    )
    async def status(self, interaction: discord.Interaction):
        """Show the status of an active fractal group"""
        await interaction.response.defer(ephemeral=True)
        
        # Check if in a fractal thread
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("❌ This command can only be used in a fractal group thread.", ephemeral=True)
            return
        
        # Check if this is an active fractal group
        group = self.active_groups.get(interaction.channel.id)
        if not group:
            await interaction.followup.send("❌ This thread is not an active fractal group.", ephemeral=True)
            return
        
        # Build status message
        status = f"# ZAO Fractal Status\n\n"
        status += f"**Group:** {interaction.channel.name}\n"
        status += f"**Facilitator:** {group.facilitator.mention}\n"
        status += f"**Current Level:** {group.current_level}\n"
        status += f"**Members:** {len(group.members)}\n"
        status += f"**Active Candidates:** {len(group.active_candidates)}\n"
        status += f"**Votes Cast:** {len(group.votes)}/{len(group.members)}\n\n"
        
        # Winners so far
        if group.winners:
            status += "**Winners:**\n"
            for level, winner in sorted(group.winners.items(), reverse=True):
                status += f"Level {level}: {winner.mention}\n"
        
        await interaction.followup.send(status, ephemeral=True)
