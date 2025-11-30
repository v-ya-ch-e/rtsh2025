import openai
import os
import json
from datetime import datetime
import time

# Set your OpenAI API key
openai.api_key = open("cred").read()  # or directly: "your-api-key-here"

SECTIONS = [
    "PRODUCTS & SERVICES (10+ firearms with specs, pricing, roadmap, supply)",
    "FINANCIAL HISTORY (two years window: P&L, balance sheets, cash flow, ratios)",
    "CUSTOMER CASE STUDIES (5+ detailed stories)",
    "COMPETITIVE LANDSCAPE (15 competitors analyzed)",
    "PARTNERSHIPS & ALLIANCES",
    "SALES DATA (quarterly by region/product)",
    "NEGOTIATION LEVERAGE POINTS"
]


def generate_section(client, section_idx, previous_context, target_words_per_section=3000):
    """Generate one section with context from previous sections"""

    section_name = SECTIONS[section_idx]
    system_prompt = f"""You are creating the definitive business intelligence profile for AnswerLio GmbH, a fictional Zurich-based defense contractor specializing in producing firearms like guns, rifles and machine guns.

Generate ONLY the content for section: ## {section_name}

Use double newlines (\\n\\n) to separate paragraphs. Make it hyper-detailed with realistic German defense industry specifics:
- 10,000 employees (2025)
- €1B revenue (2024) from government/military contracts
- Bundeswehr primary customer + NATO export ambitions
- Precision manufacturing in Swiss Alps with global supply chain

Target {target_words_per_section} words for this section. Reference previous sections consistently:
{previous_context[:4000]}

Maintain continuity in names, dates, financials, products. Include realistic military details: calibers, ROF, contract values, DoD/NATO designations, production rates. Output ONLY the section content with ## header."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Fixed model name
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate section {section_idx + 1}/{len(SECTIONS)}: {section_name}"}
            ],
            max_tokens=1000,  # Increased for 3k words
            temperature=0.7,
            top_p=0.9
        )

        content = response.choices[0].message.content.strip()
        word_count = len(content.split())

        print(f"✅ Section {section_idx + 1}/{len(SECTIONS)} '{section_name[:40]}...' → {word_count:,} words")
        return content, word_count

    except Exception as e:
        print(f"❌ Error generating section {section_idx + 1}: {e}")
        return "", 0


def generate_full_dataset():
    """Iteratively generate 40k+ word AnswerLio GmbH dataset section by section"""

    client = openai.OpenAI(api_key=openai.api_key)
    full_dataset = []
    previous_context = ""
    total_words = 0

    print("🚀 Generating AnswerLio GmbH Dataset (40k+ words, section-by-section)")
    print("=" * 80)

    for i, section in enumerate(SECTIONS):
        print(f"\n📝 Generating [{i + 1}/{len(SECTIONS)}] {section}")

        section_content, words = generate_section(client, i, previous_context)

        if section_content:
            full_dataset.append(section_content)
            total_words += words
            previous_context += f"\n\n## PREVIOUS: {section}\n{section_content[:1500]}..."  # Better context

            # Save progress
            progress_file = f"answerlio_progress_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write("\n\n".join(full_dataset))  # Fixed separator

            print(f"   📊 Progress: {total_words:,} total words | {words:,} this section")
            print(f"   💾 Saved: {progress_file}")

        # Rate limiting
        time.sleep(2)  # Increased for stability

    # Final assembly
    final_content = "\n\n".join(full_dataset)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    final_file = f"answerlio_gmbh_full_dataset_{timestamp}.md"

    with open(final_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print("\n" + "=" * 80)
    print(f"🎉 COMPLETE! {total_words:,} words generated")
    print(f"💾 Final file: {final_file}")
    print(f"📈 Words per section average: {total_words / len(SECTIONS):.0f}")
    print("\n📋 First 500 chars preview:")
    print(final_content[:500] + "...")

    return final_content, total_words


if __name__ == "__main__":
    dataset, word_count = generate_full_dataset()
