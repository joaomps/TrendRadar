#!/usr/bin/env python3
"""
Data Migration Script: Chinese Date Format → English Date Format

Migrates existing output files from Chinese date format to English format:
- Directories: 2025年11月19日 → 2025-11-19
- TXT files: 09时54分.txt → 09-54.txt

Usage:
    python migrate_output_dates.py [--dry-run] [--backup]

Options:
    --dry-run    Preview changes without applying them
    --backup     Create backup before migration
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class DateFormatMigrator:
    """Migrate output files from Chinese to English date format."""

    def __init__(self, output_dir="output", dry_run=False, backup=False):
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            'dirs_renamed': 0,
            'files_renamed': 0,
            'errors': 0
        }

    def parse_chinese_date(self, dirname):
        """
        Parse Chinese date format: 2025年11月19日
        Returns: (year, month, day) or None
        """
        pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        match = re.match(pattern, dirname)
        if match:
            year, month, day = match.groups()
            return year, month.zfill(2), day.zfill(2)
        return None

    def parse_chinese_time(self, filename):
        """
        Parse Chinese time format: 09时54分.txt
        Returns: (hour, minute) or None
        """
        pattern = r'(\d{1,2})时(\d{1,2})分\.txt$'
        match = re.match(pattern, filename)
        if match:
            hour, minute = match.groups()
            return hour.zfill(2), minute.zfill(2)
        return None

    def create_backup(self):
        """Create backup of output directory."""
        if not self.output_dir.exists():
            print(f"⚠️  Output directory {self.output_dir} does not exist")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.output_dir.parent / f"{self.output_dir.name}_backup_{timestamp}"

        print(f"📦 Creating backup: {backup_dir}")
        try:
            shutil.copytree(self.output_dir, backup_dir)
            print(f"✅ Backup created successfully")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False

    def migrate_txt_files(self, date_dir):
        """Migrate TXT files in a date directory."""
        txt_dir = date_dir / "txt"
        if not txt_dir.exists():
            return

        for txt_file in txt_dir.iterdir():
            if not txt_file.is_file():
                continue

            # Parse Chinese time format
            time_parts = self.parse_chinese_time(txt_file.name)
            if time_parts:
                hour, minute = time_parts
                new_filename = f"{hour}-{minute}.txt"
                new_path = txt_dir / new_filename

                if self.dry_run:
                    print(f"  📄 Would rename: {txt_file.name} → {new_filename}")
                else:
                    try:
                        txt_file.rename(new_path)
                        print(f"  ✅ Renamed file: {txt_file.name} → {new_filename}")
                        self.stats['files_renamed'] += 1
                    except Exception as e:
                        print(f"  ❌ Error renaming {txt_file.name}: {e}")
                        self.stats['errors'] += 1

    def migrate_directories(self):
        """Migrate date directories from Chinese to English format."""
        if not self.output_dir.exists():
            print(f"⚠️  Output directory {self.output_dir} does not exist")
            return

        # Find all directories with Chinese date format
        chinese_dirs = []
        for item in self.output_dir.iterdir():
            if item.is_dir():
                date_parts = self.parse_chinese_date(item.name)
                if date_parts:
                    chinese_dirs.append((item, date_parts))

        if not chinese_dirs:
            print("ℹ️  No directories with Chinese date format found")
            return

        print(f"📁 Found {len(chinese_dirs)} directories to migrate\n")

        # Process each directory
        for old_dir, (year, month, day) in sorted(chinese_dirs):
            new_dirname = f"{year}-{month}-{day}"
            new_dir = self.output_dir / new_dirname

            print(f"📂 Processing: {old_dir.name}")

            # First migrate TXT files within the directory
            self.migrate_txt_files(old_dir)

            # Then rename the directory itself
            if self.dry_run:
                print(f"  📁 Would rename: {old_dir.name} → {new_dirname}\n")
            else:
                try:
                    old_dir.rename(new_dir)
                    print(f"  ✅ Renamed directory: {old_dir.name} → {new_dirname}\n")
                    self.stats['dirs_renamed'] += 1
                except Exception as e:
                    print(f"  ❌ Error renaming directory: {e}\n")
                    self.stats['errors'] += 1

    def run(self):
        """Run the migration process."""
        print("=" * 60)
        print("📅 Date Format Migration Tool")
        print("=" * 60)
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"Backup: {'Enabled' if self.backup else 'Disabled'}")
        print("=" * 60)
        print()

        # Create backup if requested
        if self.backup and not self.dry_run:
            if not self.create_backup():
                print("❌ Migration aborted due to backup failure")
                return False
            print()

        # Run migration
        self.migrate_directories()

        # Print summary
        print("=" * 60)
        print("📊 Migration Summary")
        print("=" * 60)
        print(f"Directories renamed: {self.stats['dirs_renamed']}")
        print(f"Files renamed: {self.stats['files_renamed']}")
        print(f"Errors: {self.stats['errors']}")
        print("=" * 60)

        if self.dry_run:
            print("\nℹ️  This was a dry run. No changes were made.")
            print("   Run without --dry-run to apply changes.")
        elif self.stats['errors'] == 0:
            print("\n✅ Migration completed successfully!")
        else:
            print(f"\n⚠️  Migration completed with {self.stats['errors']} errors")

        return self.stats['errors'] == 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate TrendRadar output files from Chinese to English date format"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup before migration'
    )
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory path (default: output)'
    )

    args = parser.parse_args()

    migrator = DateFormatMigrator(
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        backup=args.backup
    )

    success = migrator.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
