import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
import json

st.set_page_config(
    page_title="Sortify!",
    page_icon="",
    layout="centered"
)

st.title("Welcome to Sortify!")
st.subheader("Your Personal AI Waste Segregator")

st.write(
    "Take a picture of waste and let AI identify it, "
    "classify it, and suggest responsible disposal."
)

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

waste_info = {
    "Glass": {
        "biodegradable": "Non-biodegradable",
        "bin": "🔵 BLUE BIN",
        "instruction": (
            "Separate glass for recycling where accepted. "
            "Handle broken glass safely."
        )
    },
    "Organic": {
        "biodegradable": "Biodegradable",
        "bin": "🟢 GREEN BIN",
        "instruction": (
            "Send suitable food scraps and organic waste "
            "for composting or local wet-waste collection."
        )
    },
    "Plastic": {
        "biodegradable": "Non-biodegradable",
        "bin": "🔵 BLUE BIN",
        "instruction": (
            "Keep accepted recyclable plastics clean and dry. "
            "Check local recycling rules."
        )
    },
    "Paper": {
        "biodegradable": "Biodegradable",
        "bin": "🔵 BLUE BIN",
        "instruction": (
            "Put clean, dry paper in paper recycling where accepted."
        )
    },
    "E-waste": {
        "biodegradable": "Non-biodegradable",
        "bin": "🟡 HAZARDOUS COLLECTION",
        "instruction": (
            "Take electronics to an authorized e-waste collection "
            "facility. Do not dismantle electronic devices."
        )
    },
    "Sanitary": {
        "biodegradable": "Generally non-biodegradable as a product",
        "bin": "🔴 SANITARY WASTE",
        "instruction": (
            "Wrap sanitary waste securely and follow local "
            "collection instructions."
        )
    },
    "Metal": {
        "biodegradable": "Non-biodegradable",
        "bin": "🔵 BLUE BIN",
        "instruction": (
            "Recycle suitable household metal where accepted. "
            "Industrial scrap and medical instruments may need "
            "specialized handling."
        )
    },
    "Batteries": {
        "biodegradable": "Non-biodegradable",
        "bin": "🟡 HAZARDOUS COLLECTION",
        "instruction": (
            "Keep batteries separate and take them to an authorized "
            "collection point. Never open, crush, or burn them."
        )
    }
}


picture = st.camera_input("Take a picture of your waste")

if picture is not None:
    img = Image.open(picture).convert("RGB")

    st.image(
        img,
        caption="Captured waste item",
        use_container_width=True
    )

    st.write("### AI Waste Identification")

    if st.button("Identify Waste with AI", type="primary"):

        if not api_key:
            st.error(
                "Gemini API key not found. Add GEMINI_API_KEY "
                "to .streamlit/secrets.toml and restart the app."
            )

        else:
            try:
                client = genai.Client(api_key=api_key)

                prompt = """
                You are the image-classification engine for Sortify,
                a waste segregation application.

                Examine the supplied photograph and identify the
                most prominent visible waste item.

                Choose exactly one category from:
                Glass, Organic, Plastic, Paper, E-waste,
                Sanitary, Metal, Batteries.

                Return ONLY a valid JSON object in this format:
                {
                  "item_name": "short name of the visible object",
                  "category": "one allowed category",
                  "reason": "brief visual explanation",
                  "uncertain": false
                }

                If the image does not clearly show a waste item,
                or the category cannot be determined reliably,
                set category to "Uncertain" and uncertain to true.

                Do not guess the chemical contents of a battery,
                whether a battery is rechargeable, or whether
                an object is radioactive based on appearance alone.

                Do not classify an object as a battery merely
                because it is electronic.
                """

                with st.spinner(
                    "Gemini is analysing your photo..."
                ):
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[prompt, img],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )

                result = json.loads(response.text)

                item_name = result.get(
                    "item_name", "Unknown item"
                )
                category = result.get(
                    "category", "Uncertain"
                )
                reason = result.get("reason", "")
                uncertain = result.get("uncertain", False)


                if uncertain or category not in waste_info:
                    st.warning(
                        "AI could not confidently classify this "
                        "photo. Try taking a clearer picture or "
                        "checking the category manually."
                    )

                else:
                    info = waste_info[category]

                    st.success(
                        f"Identified object: {item_name}"
                    )

                    st.write(f"**Waste type:** {category}")
                    st.write(
                        f"**Biodegradability:** "
                        f"{info['biodegradable']}"
                    )
                    st.write(f"**Suggested stream:** {info['bin']}")

                    if reason:
                        st.write(f"**Why AI chose this:** {reason}")

                    st.info(
                        f"**Disposal tip:** {info['instruction']}"
                    )

                    if category == "Batteries":
                        st.warning(
                            "A photo cannot reliably establish "
                            "whether a battery is rechargeable or "
                            "safe to reuse. Only recharge batteries "
                            "following manufacturer instructions."
                            ""
                        )

                    if category == "Metal":
                        st.caption(
                            "Confirm whether the metal is household "
                            "scrap, industrial scrap, or a medical "
                            "instrument before disposal."
                        )

                    st.caption(
                        "AI predictions can be incorrect. "
                        "Verify the result before disposing of "
                        "hazardous or unfamiliar waste."
                    )

            except json.JSONDecodeError:
                st.error(
                    "The AI response could not be read. "
                    "Please try again."
                )

            except Exception as e:
                st.error(
                    "Could not connect to Gemini. Check your API "
                    "key, internet connection, API access, and "
                    "model availability."
                )
                st.caption(f"Technical details: {e}")

st.divider()
st.caption("Be A Cutie, Do Your Duty!")

