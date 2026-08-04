#!/usr/bin/env python3
"""
TCG Release Scraper - Playwright Edition
Atualiza automaticamente as datas de lançamento dos TCGs.
Usa Playwright para sites com JavaScript pesado.
Corre via GitHub Actions diariamente.
"""

import json
import re
import sys
import asyncio
from datetime import datetime, date
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "releases.json"


def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_data(data):
    data['last_updated'] = date.today().isoformat()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Dados guardados. Última atualização: {data['last_updated']}")


async def scrape_mtg():
    """MTG via Scryfall API (não precisa de Playwright)."""
    import httpx
    releases = []
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.scryfall.com/sets", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                today = date.today()
                for s in data.get('data', []):
                    if s.get('set_type') in ['expansion', 'core', 'masters', 'draft_innovation']:
                        rd = s.get('released_at')
                        if rd:
                            rdate = date.fromisoformat(rd)
                            diff = (rdate - today).days
                            if diff > -90:  # últimos 3 meses e futuro
                                releases.append({
                                    'name': s['name'],
                                    'date': rd,
                                    'type': s['set_type']
                                })
                print(f"[MTG] {len(releases)} sets encontrados via Scryfall API")
    except Exception as e:
        print(f"[MTG] Erro: {e}")
    return releases


async def scrape_onepiece(page):
    """One Piece TCG via site oficial (EN)."""
    releases = []
    try:
        await page.goto("https://en.onepiece-cardgame.com/products/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all('.productlist-item, .product-item, [class*="product"]')
        print(f"[One Piece] {len(items)} elementos de produto encontrados")

        # Extrair texto da página toda para encontrar datas
        content = await page.content()

        # Procurar padrões de data no formato "Release DateXXXX"
        date_patterns = re.findall(r'Release Date[:\s]*([\w\s,]+\d{4}|\w+ \d{1,2},? \d{4}|\w+ \d{4})', content)
        product_patterns = re.findall(r'(BOOSTER PACK[^<]*\[[\w-]+\]|EXTRA BOOSTER[^<]*\[[\w-]+\])', content)

        for i, product in enumerate(product_patterns):
            if i < len(date_patterns):
                releases.append({
                    'name': product.strip(),
                    'date_text': date_patterns[i].strip()
                })
                print(f"  -> {product.strip()}: {date_patterns[i].strip()}")

    except Exception as e:
        print(f"[One Piece] Erro: {e}")
    return releases


async def scrape_pokemon(page):
    """Pokémon TCG - site oficial."""
    releases = []
    try:
        await page.goto("https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()

        # Procurar nomes de expansões no dropdown
        expansions = re.findall(r'<option[^>]*>([^<]+)</option>', content)
        # Filtrar expansões relevantes (Mega Evolution era, etc.)
        relevant = [e.strip() for e in expansions if any(kw in e for kw in ['Mega Evolution', 'Pitch Black', 'Chaos Rising', 'Perfect Order', 'Ascended', 'Phantasmal'])]

        if relevant:
            print(f"[Pokemon] Expansões encontradas: {relevant}")
            for exp in relevant:
                releases.append({'name': exp})
        else:
            print("[Pokemon] Nenhuma expansão nova encontrada no HTML")

    except Exception as e:
        print(f"[Pokemon] Erro: {e}")
    return releases


async def scrape_riftbound(page):
    """Riftbound (League of Legends TCG)."""
    releases = []
    try:
        await page.goto("https://www.riftbound.com", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        content = await page.content()

        # Procurar menções a sets/produtos
        news_items = re.findall(r'(\d{4}-\d{2}-\d{2})T[^"]*"[^>]*>([^<]+)', content)
        print(f"[Riftbound] {len(news_items)} news items encontrados")

        for date_str, title in news_items:
            if any(kw in title.lower() for kw in ['product', 'set', 'release', 'vendetta', 'origin']):
                releases.append({'name': title, 'date': date_str})
                print(f"  -> {title}: {date_str}")

    except Exception as e:
        print(f"[Riftbound] Erro: {e}")
    return releases


async def scrape_lorcana(page):
    """Disney Lorcana."""
    releases = []
    try:
        await page.goto("https://www.disneylorcana.com/en-US/products", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)

        content = await page.content()
        # Procurar nomes de sets
        sets_found = re.findall(r'(Set \d+|Azurite Sea|Archazia|Shimmering Skies)', content, re.IGNORECASE)
        if sets_found:
            print(f"[Lorcana] Sets encontrados: {list(set(sets_found))}")
        else:
            print("[Lorcana] Nenhum set encontrado no HTML")

    except Exception as e:
        print(f"[Lorcana] Erro: {e}")
    return releases


async def scrape_dragonball(page):
    """Dragon Ball Super Card Game - Fusion World."""
    releases = []
    try:
        await page.goto("https://www.dbs-cardgame.com/fw/us/product/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        # Procurar FB-XX sets
        fb_sets = re.findall(r'(FB-\d+[^<]*)', content)
        if fb_sets:
            print(f"[Dragon Ball] Sets encontrados: {fb_sets[:10]}")
        else:
            print("[Dragon Ball] Nenhum set encontrado")

    except Exception as e:
        print(f"[Dragon Ball] Erro: {e}")
    return releases


async def scrape_yugioh(page):
    """Yu-Gi-Oh! TCG."""
    releases = []
    try:
        await page.goto("https://www.yugioh-card.com/en/products/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)

        content = await page.content()
        # Procurar produtos com datas
        products = re.findall(r'<h3[^>]*>([^<]+)</h3>', content)
        dates = re.findall(r'Release:\s*(\w+ \d{1,2},? \d{4})', content)

        print(f"[Yu-Gi-Oh!] {len(products)} produtos, {len(dates)} datas encontradas")
        for i, prod in enumerate(products[:10]):
            if i < len(dates):
                releases.append({'name': prod.strip(), 'date_text': dates[i]})
                print(f"  -> {prod.strip()}: {dates[i]}")

    except Exception as e:
        print(f"[Yu-Gi-Oh!] Erro: {e}")
    return releases


def update_mtg_data(data, scraped):
    """Atualiza dados do MTG com info do Scryfall."""
    if not scraped:
        return False

    mtg = next((t for t in data['tcgs'] if t['id'] == 'mtg'), None)
    if not mtg:
        return False

    existing_sets = {r.get('set', '') for r in mtg['releases']}
    updated = False

    for release in scraped:
        if release['name'] not in existing_sets:
            # Adicionar Booster Box e Collector Box para novos sets
            for product_type, product_name in [('Booster Box', 'Play Booster Box'), ('Collector Box', 'Collector Booster Box')]:
                mtg['releases'].append({
                    'set': release['name'],
                    'name': product_name,
                    'type': product_type,
                    'regions': {
                        'usa': {'date': release['date']},
                        'europe': {'date': release['date']},
                        'japan': {'date': release['date']}
                    }
                })
            print(f"[MTG] Novo set adicionado: {release['name']} ({release['date']})")
            updated = True

    return updated


async def main():
    """Função principal."""
    print("=" * 60)
    print("TCG Release Scraper - Playwright Edition")
    print(f"Data: {date.today().isoformat()}")
    print("=" * 60)

    data = load_data()
    updated = False

    # MTG - só precisa de HTTP (sem Playwright)
    print("\n--- Magic: The Gathering (Scryfall API) ---")
    mtg_releases = await scrape_mtg()
    if update_mtg_data(data, mtg_releases):
        updated = True

    # Playwright para os restantes
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            print("\n--- One Piece TCG ---")
            await scrape_onepiece(page)

            print("\n--- Pokémon TCG ---")
            await scrape_pokemon(page)

            print("\n--- Riftbound ---")
            await scrape_riftbound(page)

            print("\n--- Disney Lorcana ---")
            await scrape_lorcana(page)

            print("\n--- Dragon Ball Super ---")
            await scrape_dragonball(page)

            print("\n--- Yu-Gi-Oh! TCG ---")
            await scrape_yugioh(page)

            await browser.close()

    except ImportError:
        print("\n[AVISO] Playwright não instalado. A usar apenas Scryfall API.")
        print("Para instalar: pip install playwright && playwright install chromium")
    except Exception as e:
        print(f"\n[ERRO] Playwright falhou: {e}")

    # Guardar dados
    save_data(data)

    print("\n" + "=" * 60)
    print("Scraping concluído!")
    if updated:
        print("DADOS ATUALIZADOS - novos lançamentos encontrados!")
    else:
        print("Sem novos dados (manter dados atuais)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
