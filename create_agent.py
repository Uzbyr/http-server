#!/usr/bin/env python3

import os
import sys
sys.path.append('src')
from mistral_service import MistralAgentService

def get_user_input(prompt, default=None):
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("This field is required. Please enter a value.")

def main():
    """Interactive agent creation script"""
    print("🤖 Mistral Agent Creator")
    print("=" * 30)
    print()
    
    try:
        # Initialize the Mistral service
        mistral_service = MistralAgentService()
        print("✅ Connected to Mistral API")
        print()
        
        # Get agent details from user
        print("Let's create your Mistral agent!")
        print()
        
        name = get_user_input("Agent name")
        description = get_user_input("Agent description")
        instructions = get_user_input("System instructions (how should the agent behave?)")
        
        print()
        print("Optional settings (press Enter for defaults):")
        model = get_user_input("Model", "mistral-medium-2505")
        
        # Get temperature with validation
        while True:
            try:
                temp_input = get_user_input("Temperature (0.0-2.0)", "0.7")
                temperature = float(temp_input)
                if 0.0 <= temperature <= 2.0:
                    break
                else:
                    print("Temperature must be between 0.0 and 2.0")
            except ValueError:
                print("Please enter a valid number")
        
        print()
        print("Creating agent...")
        print("-" * 30)
        
        # Create the agent
        result = mistral_service.create_agent(
            name=name,
            description=description,
            instructions=instructions,
            model=model,
            temperature=temperature
        )
        
        # Display result
        if "isError" in result and result["isError"]:
            print("❌ Error creating agent:")
            print(result["content"][0]["text"])
        else:
            print("✅ Agent created successfully!")
            print()
            print(result["content"][0]["text"])
            print()
            print("🎉 Your agent is ready to use!")
    
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
