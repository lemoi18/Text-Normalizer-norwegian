#!/usr/bin/env python3
"""
TTS Dataset Normalizer

This script reads the original TTS dataset and creates a new normalized version
where all text is processed through the Norwegian text normalizer while preserving
the original format: filename|text|speaker_id

Usage:
    python create_normalized_dataset.py

This will create a new file 'tts_dataset_normalized.txt' with all text normalized.
"""

import sys
import os
from normalize import normalize as integrated_normalize

def load_original_dataset(filepath):
    """Load the original TTS dataset."""
    samples = []

    if not os.path.exists(filepath):
        print(f"Error: Dataset file '{filepath}' not found!")
        return samples

    print(f"Loading original dataset from {filepath}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    filename = parts[0]
                    text = parts[1]
                    speaker_id = parts[2] if len(parts) > 2 else "1"

                    samples.append({
                        'line_num': line_num,
                        'filename': filename,
                        'text': text,
                        'speaker_id': speaker_id
                    })

    print(f"Loaded {len(samples)} samples from original dataset")
    return samples

def normalize_text(text):
    """Normalize text using the integrated normalizer."""
    try:
        return integrated_normalize(text)
    except Exception as e:
        # If normalization fails, return original text
        print(f"Warning: Normalization failed for text: {text[:50]}... Error: {e}")
        return text

def create_normalized_dataset(samples, output_filepath):
    """Create the normalized dataset file."""
    print(f"Creating normalized dataset: {output_filepath}")

    normalized_count = 0
    unchanged_count = 0

    with open(output_filepath, 'w', encoding='utf-8') as f:
        for sample in samples:
            original_text = sample['text']
            normalized_text = normalize_text(original_text)

            # Write in the same format: filename|text|speaker_id
            line = f"{sample['filename']}|{normalized_text}|{sample['speaker_id']}"
            f.write(line + '\n')

            # Track changes
            if original_text != normalized_text:
                normalized_count += 1
            else:
                unchanged_count += 1

    return normalized_count, unchanged_count

def show_normalization_examples(samples, num_examples=10):
    """Show examples of normalization changes."""
    print(f"\nNormalization Examples (showing first {num_examples}):")
    print("=" * 80)

    examples_shown = 0
    for sample in samples:
        original = sample['text']
        normalized = normalize_text(original)

        if original != normalized and examples_shown < num_examples:
            print(f"\nExample {examples_shown + 1}:")
            print(f"  Line:     {sample['line_num']}")
            print(f"  File:     {sample['filename']}")
            print(f"  Original: {original}")
            print(f"  Normalized: {normalized}")
            examples_shown += 1

    print("\n" + "=" * 80)

def generate_statistics(samples, normalized_count, unchanged_count):
    """Generate statistics about the normalization process."""
    total_samples = len(samples)

    print(f"\nNormalization Statistics:")
    print(f"  Total samples processed:     {total_samples}")
    print(f"  Samples with changes:       {normalized_count} ({normalized_count/total_samples*100:.1f}%)")
    print(f"  Samples unchanged:         {unchanged_count} ({unchanged_count/total_samples*100:.1f}%)")

    # Calculate text length changes
    original_total_length = sum(len(sample['text']) for sample in samples)
    normalized_total_length = sum(len(normalize_text(sample['text'])) for sample in samples)

    if original_total_length > 0:
        length_ratio = normalized_total_length / original_total_length
        print(f"  Original text length:        {original_total_length:,} characters")
    print(f"  Normalized text length:      {normalized_total_length:,} characters")
    if original_total_length > 0:
        print(f"  Length expansion ratio:       {length_ratio:.2f}x")

def main():
    """Main function to create normalized TTS dataset."""
    print("TTS Dataset Normalizer")
    print("=" * 50)

    # File paths
    input_file = 'tts_dataset.txt'
    output_file = 'tts_dataset_normalized.txt'

    # Load original dataset
    samples = load_original_dataset(input_file)
    if not samples:
        print("No samples loaded. Exiting.")
        return

    # Show some examples before processing
    print(f"\nPreview: Processing {len(samples)} samples...")

    # Create normalized dataset
    normalized_count, unchanged_count = create_normalized_dataset(samples, output_file)

    # Show examples of changes
    show_normalization_examples(samples)

    # Generate statistics
    generate_statistics(samples, normalized_count, unchanged_count)

    # Success message
    print(f"\nSuccess!")
    print(f"   Original dataset:  {input_file}")
    print(f"   Normalized dataset: {output_file}")
    print(f"   Samples processed: {len(samples)}")
    print(f"   Normalized: {normalized_count}")
    print(f"   Unchanged: {unchanged_count}")

    print(f"\nYou can now use '{output_file}' with your TTS system!")
    print("   The normalized text will provide better pronunciation for Norwegian text.")

if __name__ == '__main__':
    main()