#!/usr/bin/env python3
"""
Generate individualized consent form HTML files from a default template
using site-specific overrides from a JSON mapping file.
"""

import argparse
import json
import logging
import os
import re
import sys
from typing import Dict, Tuple, Optional


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def resolve_default_path(path: str, mapping_hint_dir: Optional[str]) -> str:
    """
    Resolve a potentially relative path. Try as given; if not found and we have a mapping
    directory hint, try relative to that directory; finally try relative to the project
    structure ('06_input_institutions').
    """
    candidate_paths = []

    # 1) As provided (relative to current working directory)
    candidate_paths.append(os.path.abspath(os.path.expanduser(path)))

    # 2) Relative to mapping hint directory (if available)
    if mapping_hint_dir:
        candidate_paths.append(os.path.abspath(os.path.join(mapping_hint_dir, path)))

    # 3) Relative to '06_input_institutions' (project-typical layout)
    if not path.startswith("06_input_institutions" + os.sep):
        candidate_paths.append(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "06_input_institutions", path))
        )

    for candidate in candidate_paths:
        if os.path.exists(candidate):
            return candidate
    # If nothing exists, return the first candidate (best-effort) so the caller gets a clear error.
    return candidate_paths[0]


def load_mapping(mapping_path: str) -> Tuple[Dict[str, Dict], str]:
    with open(mapping_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping_dir = os.path.dirname(mapping_path)
    return data, mapping_dir


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_text_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def replace_between_markers(
    html: str,
    start_marker: str,
    end_marker: str,
    replacement_html: str,
) -> Tuple[str, bool]:
    """
    Replace content between comment markers if present.
    Returns (new_html, used_markers).
    """
    pattern = re.compile(
        rf"<!--\s*{re.escape(start_marker)}\s*-->(?P<body>[\s\S]*?)<!--\s*{re.escape(end_marker)}\s*-->",
        flags=re.IGNORECASE,
    )

    def _repl(m: re.Match) -> str:
        # Normalize markers casing/spacing in output.
        return f"<!-- {start_marker} -->\n{replacement_html}\n<!-- {end_marker} -->"

    new_html, count = pattern.subn(_repl, html, count=1)
    return new_html, count > 0


def replace_section_after_heading(
    html: str,
    heading_text: str,
    replacement_html: str,
) -> Tuple[str, bool]:
    """
    Replace the content immediately following a <h3>HEADING</h3> up to the next heading or major boundary.
    Returns (new_html, replaced).
    This is a tolerant fallback that allows whitespace and attribute variations in the <h3>.
    """
    pattern = re.compile(
        r"(?P<prefix><h3[^>]*>\s*" + re.escape(heading_text) + r"\s*</h3>\s*)(?P<section>[\s\S]*?)(?=<h[23][^>]*>|</section>|</div>|<button|<br|</body>|</html>|\Z)",
        flags=re.IGNORECASE,
    )

    def _repl(m: re.Match) -> str:
        return m.group("prefix") + replacement_html + "\n"

    new_html, count = pattern.subn(_repl, html, count=1)
    return new_html, count > 0


def replace_between_headings(
    html: str,
    start_heading_text: str,
    end_heading_text: str,
    replacement_html: str,
) -> Tuple[str, bool]:
    """
    Replace the content between two specific <h3>... </h3> headings.
    Matches the first occurrence of the start heading and replaces everything
    until just before the next occurrence of the end heading.
    Returns (new_html, replaced).
    """
    pattern = re.compile(
        r"(?P<prefix><h3[^>]*>\s*" + re.escape(start_heading_text) + r"\s*</h3>\s*)(?P<section>[\s\S]*?)(?=(<h3[^>]*>\s*" + re.escape(end_heading_text) + r"\s*</h3>))",
        flags=re.IGNORECASE,
    )

    def _repl(m: re.Match) -> str:
        return m.group("prefix") + replacement_html + "\n"

    new_html, count = pattern.subn(_repl, html, count=1)
    return new_html, count > 0


def replace_between_heading_and_h2(
    html: str,
    start_h3_text: str,
    end_h2_contains_text: str,
    replacement_html: str,
) -> Tuple[str, bool]:
    """
    Replace content starting after an <h3>START</h3> heading up to (but not including)
    the next <h2> that contains END text anywhere within it.
    Useful for replacing a section that spans until the next major section.
    Returns (new_html, replaced).
    """
    pattern = re.compile(
        r"(?P<prefix><h3[^>]*>\s*" + re.escape(start_h3_text) + r"\s*</h3>\s*)(?P<section>[\s\S]*?)(?=(<h2[^>]*>[\s\S]*?" + re.escape(end_h2_contains_text) + r"[\s\S]*?</h2>))",
        flags=re.IGNORECASE,
    )

    def _repl(m: re.Match) -> str:
        return m.group("prefix") + replacement_html + "\n"

    new_html, count = pattern.subn(_repl, html, count=1)
    return new_html, count > 0


def perform_conditional_replacements(
    site: str,
    base_html: str,
    site_cfg: Dict[str, Optional[str]],
    logger: logging.Logger,
) -> str:
    """
    Apply conditional replacements to base_html using either markers or fallback regex,
    depending on availability and site flags.
    """
    result_html = base_html

    # 1b: Reimbursement
    reimburse_yes = str(site_cfg.get("1a_individual_reimbursement", "no")).lower() == "yes"
    reimburse_text = site_cfg.get("1a_individual_reimbursement_text")
    if reimburse_yes:
        if not reimburse_text:
            logger.warning(
                "%s: 1a_individual_reimbursement is 'yes' but 1a_individual_reimbursement_text is missing.",
                site,
            )
        else:
            # Try markers first
            updated, used = replace_between_markers(
                result_html, "REIMBURSEMENT_START", "REIMBURSEMENT_END", reimburse_text
            )
            if used:
                logger.debug("%s: Reimbursement replaced via markers.", site)
                result_html = updated
            else:
                # Fallback: section after heading 'Aufwandsentschädigung'
                updated, ok = replace_section_after_heading(
                    result_html, "Aufwandsentschädigung", reimburse_text
                )
                if ok:
                    logger.debug("%s: Reimbursement replaced via heading fallback.", site)
                    result_html = updated
                else:
                    logger.warning(
                        "%s: Could not locate reimbursement section (markers or heading).", site
                    )

    # 1c: Data protection (responsible person / institution)
    dpo_yes = str(site_cfg.get("1b_individual_data_protection", "no")).lower() == "yes"
    dpo_text = site_cfg.get("1b_individual_data_protection_text")
    if dpo_yes:
        if not dpo_text:
            logger.warning(
                "%s: 1b_individual_data_protection is 'yes' but 1b_individual_data_protection_text is missing.",
                site,
            )
        else:
            # Prefer exact replacement between the 'Verantwortliche' and 'Rechtsgrundlage' headings
            updated, ok = replace_between_headings(
                result_html, "Verantwortliche", "Rechtsgrundlage", dpo_text
            )
            if ok:
                logger.debug("%s: Data protection replaced between headings.", site)
                result_html = updated
            else:
                # Try explicit comment markers if present
                updated, used = replace_between_markers(
                    result_html, "DPO_START", "DPO_END", dpo_text
                )
                if used:
                    logger.debug("%s: Data protection replaced via markers.", site)
                    result_html = updated
                else:
                    # Fallback to generic "after heading until next section" replacement
                    updated, ok2 = replace_section_after_heading(
                        result_html, "Verantwortliche", dpo_text
                    )
                    if ok2:
                        logger.debug("%s: Data protection replaced via heading fallback.", site)
                        result_html = updated
                    else:
                        logger.warning(
                            "%s: Could not locate data protection section (between headings, markers, or generic heading fallback).",
                            site,
                        )

    # 1d: Complaint rights
    complain_yes = str(site_cfg.get("1c_individual_complain", "no")).lower() == "yes"
    complain_text = site_cfg.get("1c_individual_complain_text")
    if complain_yes:
        if not complain_text:
            logger.warning(
                "%s: 1c_individual_complain is 'yes' but 1c_individual_complain_text is missing.",
                site,
            )
        else:
            # Prefer exact replacement between 'Beschwerderecht' and the next H2 containing 'Einwilligungserklärung'
            updated, ok = replace_between_heading_and_h2(
                result_html, "Beschwerderecht", "Einwilligungserklärung", complain_text
            )
            if ok:
                logger.debug("%s: Complaint section replaced between headings (h3->h2).", site)
                result_html = updated
            else:
                # Try explicit comment markers if present
                updated, used = replace_between_markers(
                    result_html, "COMPLAIN_START", "COMPLAIN_END", complain_text
                )
                if used:
                    logger.debug("%s: Complaint section replaced via markers.", site)
                    result_html = updated
                else:
                    # Fallback to replacing after the 'Beschwerderecht' heading until next section
                    updated, ok2 = replace_section_after_heading(
                        result_html, "Beschwerderecht", complain_text
                    )
                    if ok2:
                        logger.debug("%s: Complaint section replaced via heading fallback.", site)
                        result_html = updated
                    else:
                        logger.warning(
                            "%s: Could not locate complaint section (between headings, markers, or generic heading fallback).",
                            site,
                        )

    return result_html


def determine_output_path(
    site: str,
    site_cfg: Dict[str, Optional[str]],
    mapping_dir: str,
    template_path: str,
    outdir: Optional[str],
) -> str:
    """
    Determine where to write the generated HTML file.

    - If --outdir is provided, write into that directory (creating it if needed),
      using either the basename from the mapping (if present) or a default
      'consent_form_<site>.html' filename.
    - Otherwise, write into the *mapping directory* (where the JSON mapping
      file lives, i.e., your 'consent_forms' folder), again using the mapping
      basename if present or the default filename.

    Note: This intentionally ignores any absolute/relative paths specified in
    '0_html_consent_form_location' beyond using their basename, so that all
    files end up next to the mapping (e.g. 'consent_forms') unless --outdir is used.
    """
    configured_path = site_cfg.get("0_html_consent_form_location")

    # 1) Explicit output directory (CLI flag takes precedence)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        if configured_path:
            basename = os.path.basename(configured_path)
        else:
            basename = f"consent_form_{site}.html"
        return os.path.abspath(os.path.join(outdir, basename))

    # 2) Default: write into the *mapping directory* (e.g. 'consent_forms')
    base_dir = mapping_dir
    if configured_path:
        basename = os.path.basename(configured_path)
    else:
        basename = f"consent_form_{site}.html"
    return os.path.abspath(os.path.join(base_dir, basename))


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build individualized consent forms from a default template and a site mapping."
    )
    parser.add_argument(
        "--mapping",
        default="consent_forms/combined_mapping.json",
        help="Path to the JSON mapping file (default: consent_forms/combined_mapping.json)",
    )
    parser.add_argument(
        "--template",
        default="defaults/consent_form_default.html",
        help="Path to the default consent form HTML template "
             "(default: defaults/consent_form_default.html)",
    )
    parser.add_argument(
        "--outdir",
        default=None,
        help="Optional directory to place all generated files (overrides mapping locations).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without writing files.",
    )

    args = parser.parse_args(argv)
    configure_logging(args.verbose)
    logger = logging.getLogger("build_consent")

    # Resolve mapping path (try as provided, then try typical project location).
    mapping_path_candidates = [
        os.path.abspath(os.path.expanduser(args.mapping)),
        os.path.abspath(os.path.join(os.path.dirname(__file__), args.mapping)),
    ]
    mapping_path = None
    for candidate in mapping_path_candidates:
        if os.path.exists(candidate):
            mapping_path = candidate
            break
    if mapping_path is None:
        print(f"ERROR: Mapping file not found: {args.mapping}", file=sys.stderr)
        return 1

    mapping, mapping_dir = load_mapping(mapping_path)

    # Resolve template path robustly
    template_path = resolve_default_path(args.template, mapping_dir)
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found: {args.template}", file=sys.stderr)
        return 1

    base_template = read_text_file(template_path)

    generated_count = 0
    skipped_count = 0

    for site, site_cfg in mapping.items():
        if site.lower() == "default":
            continue

        # Build individualized content by applying conditional replacements
        individualized_html = perform_conditional_replacements(
            site=site,
            base_html=base_template,
            site_cfg=site_cfg,
            logger=logger,
        )

        # Determine output path and write (unless dry-run)
        out_path = determine_output_path(
            site=site,
            site_cfg=site_cfg,
            mapping_dir=mapping_dir,
            template_path=template_path,
            outdir=os.path.abspath(os.path.expanduser(args.outdir)) if args.outdir else None,
        )
        out_dir = os.path.dirname(out_path)
        if not args.dry_run:
            os.makedirs(out_dir, exist_ok=True)
            write_text_file(out_path, individualized_html)
            print(f"Generated: {site} -> {out_path}")
        else:
            print(f"[Dry-run] Would generate: {site} -> {out_path}")

        generated_count += 1

    print(f"Done. Generated: {generated_count}, Skipped: {skipped_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


