import openai
import os
import re
import json
from typing import Tuple, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"
        
        # Define the conversation flow
        self.flow_steps = {
            "zip_code": {
                "prompt": "What's your ZIP code?",
                "validation": self._validate_zip_code,
                "next": "full_name"
            },
            "full_name": {
                "prompt": "Great! What's your full name?",
                "validation": self._validate_name,
                "next": "email"
            },
            "email": {
                "prompt": "Thanks! What's your email address?",
                "validation": self._validate_email,
                "next": "vehicle_start"
            },
            "vehicle_start": {
                "prompt": "Now let's add your vehicle information. Would you like to provide the VIN or the Year, Make, and Body Type?",
                "next": "vehicle_info"
            },
            "vehicle_info": {
                "prompt": "Please provide either:\n1. Your vehicle's VIN number, or\n2. Year, Make, and Body Type (e.g., '2022 Toyota Camry Sedan')",
                "validation": self._validate_vehicle_info,
                "next": "vehicle_use"
            },
            "vehicle_use": {
                "prompt": "How is this vehicle primarily used? (commuting, commercial, farming, or business)",
                "validation": self._validate_vehicle_use,
                "next": "blind_spot"
            },
            "blind_spot": {
                "prompt": "Is this vehicle equipped with blind spot warning? (Yes or No)",
                "validation": self._validate_yes_no,
                "next": "vehicle_use_details"
            },
            "vehicle_use_details": {
                "dynamic": True,  # This step changes based on vehicle use
            },
            "commute_days": {
                "prompt": "How many days per week do you use this vehicle for commuting?",
                "validation": self._validate_days,
                "next": "commute_miles"
            },
            "commute_miles": {
                "prompt": "What's the one-way distance in miles to work/school?",
                "validation": self._validate_miles,
                "next": "add_another_vehicle"
            },
            "annual_mileage": {
                "prompt": "What's the estimated annual mileage for this vehicle?",
                "validation": self._validate_mileage,
                "next": "add_another_vehicle"
            },
            "add_another_vehicle": {
                "prompt": "Would you like to add another vehicle? (Yes or No)",
                "validation": self._validate_yes_no,
                "next": "license_type"  # or back to vehicle_info if yes
            },
            "license_type": {
                "prompt": "What type of US driver's license do you have? (Foreign, Personal, or Commercial)",
                "validation": self._validate_license_type,
                "next": "license_status"
            },
            "license_status": {
                "prompt": "What's your license status? (Valid or Suspended)",
                "validation": self._validate_license_status,
                "next": "complete"
            },
            "complete": {
                "prompt": "Thank you! I've collected all the necessary information. Your onboarding is complete!"
            }
        }
    
    async def get_greeting(self) -> str:
        """Get initial greeting message"""
        return "Hello! I'm here to help you complete your onboarding. Let's start by collecting some basic information. What's your ZIP code?"
    
    async def process_message(self, 
                            message: str, 
                            current_step: str, 
                            session_data: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Process user message and return response, next step, and extracted data"""
        
        # Get current step configuration
        step_config = self.flow_steps.get(current_step, {})
        
        # Handle dynamic steps
        if step_config.get("dynamic"):
            return await self._handle_dynamic_step(message, current_step, session_data)
        
        # Validate input if validation exists
        extracted_data = {}
        validation_func = step_config.get("validation")
        
        if validation_func:
            is_valid, cleaned_value, error_message = validation_func(message)
            
            if not is_valid:
                # Use AI to generate a friendly error message
                response = await self._generate_error_response(error_message, current_step)
                return response, current_step, {}
            
            # Store the validated data
            extracted_data[current_step] = cleaned_value
        else:
    # If no validation function and has a next step, just move forward
            if "next" in step_config:
                next_step = step_config["next"]
                if next_step in self.flow_steps:
                    response = self.flow_steps[next_step].get("prompt", "")
                    response = await self._enhance_response(response, {})
                    return response, next_step, {}
        
        # Determine next step
        next_step = self._determine_next_step(current_step, message, session_data)
        
        # Generate response for next step
        if next_step in self.flow_steps:
            response = self.flow_steps[next_step].get("prompt", "")
            
            # Use AI to make the response more conversational
            response = await self._enhance_response(response, extracted_data)
        else:
            response = "Thank you for providing that information."
        
        return response, next_step, extracted_data
    
    def _determine_next_step(self, current_step: str, message: str, session_data: Dict[str, Any]) -> str:
        """Determine the next step in the flow"""
        step_config = self.flow_steps.get(current_step, {})
        
        # Handle special cases
        if current_step == "add_another_vehicle":
            if self._is_affirmative(message):
                return "vehicle_info"
            else:
                return "license_type"
        
        if current_step == "blind_spot":
            vehicle_use = session_data.get("vehicle_use", "").lower()
            if vehicle_use == "commuting":
                return "commute_days"
            elif vehicle_use in ["commercial", "farming", "business"]:
                return "annual_mileage"
            else:
                return "add_another_vehicle"
        
        if current_step == "license_type":
            license_type = message.lower()
            if license_type in ["personal", "commercial"]:
                return "license_status"
            else:
                return "complete"
        
        return step_config.get("next", "complete")
    
    async def _handle_dynamic_step(self, 
                                 message: str, 
                                 current_step: str, 
                                 session_data: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """Handle dynamic flow steps"""
        if current_step == "vehicle_use_details":
            vehicle_use = session_data.get("vehicle_use", "").lower()
            
            if vehicle_use == "commuting":
                next_step = "commute_days"
                response = self.flow_steps["commute_days"]["prompt"]
            elif vehicle_use in ["commercial", "farming", "business"]:
                next_step = "annual_mileage"
                response = self.flow_steps["annual_mileage"]["prompt"]
            else:
                next_step = "add_another_vehicle"
                response = self.flow_steps["add_another_vehicle"]["prompt"]
            
            return response, next_step, {}
        
        return "I'm not sure how to proceed. Let me help you.", current_step, {}
    
    async def _generate_error_response(self, error_message: str, current_step: str) -> str:
        """Generate a friendly error response using AI"""
        prompt = f"""
        The user provided invalid input for {current_step.replace('_', ' ')}.
        Error: {error_message}
        
        Generate a friendly, helpful response that:
        1. Acknowledges their input
        2. Explains what's needed
        3. Gives an example if helpful
        4. Asks them to try again
        
        Keep it conversational and helpful, not robotic.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly onboarding assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except:
            return f"I couldn't process that. {error_message} Please try again."
    
    async def _enhance_response(self, base_response: str, extracted_data: Dict[str, Any]) -> str:
        """Enhance response to be more conversational"""
        if not extracted_data:
            return base_response
        
        prompt = f"""
        The user just provided: {json.dumps(extracted_data)}
        
        Enhance this response to acknowledge what they said and then ask the next question:
        "{base_response}"
        
        Keep it natural, friendly, and conversational. Don't be overly enthusiastic.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly onboarding assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except:
            return base_response
    
    # Validation functions
    def _validate_zip_code(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate ZIP code"""
        cleaned = re.sub(r'\D', '', value)
        if len(cleaned) == 5 or (len(cleaned) == 9 and cleaned[5:].isdigit()):
            return True, cleaned[:5], None
        return False, None, "Please provide a valid 5-digit ZIP code"
    
    def _validate_name(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate full name"""
        cleaned = value.strip()
        if len(cleaned) >= 2 and ' ' in cleaned:
            return True, cleaned, None
        return False, None, "Please provide your full name (first and last name)"
    
    def _validate_email(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate email address"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        cleaned = value.strip().lower()
        if re.match(email_pattern, cleaned):
            return True, cleaned, None
        return False, None, "Please provide a valid email address"
    
    def _validate_vehicle_info(self, value: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Validate vehicle information (VIN or Year/Make/Body)"""
        cleaned = value.strip()
        
        # Check if it's a VIN (17 characters, alphanumeric)
        vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
        if re.match(vin_pattern, cleaned.upper()):
            return True, {"vin": cleaned.upper()}, None
        
        # Try to parse Year/Make/Body
        parts = cleaned.split()
        if len(parts) >= 3:
            try:
                year = int(parts[0])
                if 1900 <= year <= 2030:
                    return True, {
                        "year": year,
                        "make": parts[1],
                        "body_type": " ".join(parts[2:])
                    }, None
            except ValueError:
                pass
        
        return False, None, "Please provide either a 17-character VIN or Year, Make, and Body Type"
    
    def _validate_vehicle_use(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate vehicle use"""
        valid_uses = ["commuting", "commercial", "farming", "business"]
        cleaned = value.strip().lower()
        
        for use in valid_uses:
            if use in cleaned:
                return True, use, None
        
        return False, None, "Please specify: commuting, commercial, farming, or business"
    
    def _validate_yes_no(self, value: str) -> Tuple[bool, Optional[bool], Optional[str]]:
        """Validate yes/no response"""
        cleaned = value.strip().lower()
        if cleaned in ["yes", "y", "yeah", "yep", "sure", "ok", "okay"]:
            return True, True, None
        elif cleaned in ["no", "n", "nope", "nah"]:
            return True, False, None
        return False, None, "Please answer Yes or No"
    
    def _validate_days(self, value: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Validate days per week"""
        try:
            days = int(re.sub(r'\D', '', value))
            if 0 <= days <= 7:
                return True, days, None
        except ValueError:
            pass
        return False, None, "Please provide a number between 0 and 7"
    
    def _validate_miles(self, value: str) -> Tuple[bool, Optional[float], Optional[str]]:
        """Validate miles"""
        try:
            miles = float(re.sub(r'[^\d.]', '', value))
            if 0 <= miles <= 500:
                return True, miles, None
        except ValueError:
            pass
        return False, None, "Please provide a valid distance in miles"
    
    def _validate_mileage(self, value: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """Validate annual mileage"""
        try:
            mileage = int(re.sub(r'\D', '', value))
            if 0 <= mileage <= 200000:
                return True, mileage, None
        except ValueError:
            pass
        return False, None, "Please provide a valid annual mileage"
    
    def _validate_license_type(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate license type"""
        valid_types = ["foreign", "personal", "commercial"]
        cleaned = value.strip().lower()
        
        for license_type in valid_types:
            if license_type in cleaned:
                return True, license_type, None
        
        return False, None, "Please specify: Foreign, Personal, or Commercial"
    
    def _validate_license_status(self, value: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate license status"""
        cleaned = value.strip().lower()
        if "valid" in cleaned:
            return True, "valid", None
        elif "suspend" in cleaned:
            return True, "suspended", None
        return False, None, "Please specify: Valid or Suspended"
    
    def _is_affirmative(self, value: str) -> bool:
        """Check if response is affirmative"""
        affirmative = ["yes", "y", "yeah", "yep", "sure", "ok", "okay"]
        return value.strip().lower() in affirmative