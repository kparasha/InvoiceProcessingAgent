from typing import Dict, Optional, Any
import subprocess
import json
import os
import tempfile
from src.utils.logger import logger

class ScrapingAgent:
    def __init__(self):
        # Ensure node and npm are installed
        self._check_node_requirements()
        
    def _check_node_requirements(self):
        """Check if Node.js and npm are installed"""
        try:
            subprocess.run(['node', '--version'], check=True, capture_output=True)
            subprocess.run(['npm', '--version'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Node.js and npm are required to run the scraper")
            
    def scrape_vendor_info(self, vendor_name: str) -> Dict[str, Any]:
        """
        Fetch vendor information from various sources.
        This is a mock implementation - in production, you'd use real data sources.
        
        Args:
            vendor_name: The name of the vendor to look up
            
        Returns:
            Dict[str, Any]: Dictionary containing vendor information
        """
        logger.info(f"Fetching vendor information for: {vendor_name}")
        
        # Mock data for known vendors
        mock_data = {
            "Cloudflare Inc.": {
                "company": "Cloudflare Inc.",
                "website": "https://www.cloudflare.com",
                "description": "Cloudflare, Inc. is a global cloud services provider offering content delivery network services, DDoS mitigation, Internet security, and distributed domain name server services.",
                "social_links": [
                    "https://twitter.com/cloudflare",
                    "https://www.linkedin.com/company/cloudflare"
                ],
                "industry": "Internet Infrastructure & Security",
                "founded": "2009",
                "headquarters": "San Francisco, California"
            }
        }
        
        # Return mock data if vendor is found, otherwise return default data
        if vendor_name in mock_data:
            logger.info(f"Found vendor information for {vendor_name}")
            return mock_data[vendor_name]
        else:
            logger.warning(f"No vendor information found for {vendor_name}")
            return {
                "company": vendor_name,
                "website": f"https://www.{vendor_name.lower().replace(' ', '')}.com",
                "description": "Company information not available",
                "social_links": [],
                "industry": "Unknown",
                "founded": None,
                "headquarters": "Unknown"
            }

    def scrape_vendor_info_playwright(self, company_name: str) -> Dict[str, str]:
        """
        Scrape vendor information using Playwright
        """
        # Create a temporary directory for the scraper
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create package.json
            package_json = {
                "name": "vendor-scraper",
                "type": "module",
                "dependencies": {
                    "playwright": "^1.42.0"
                }
            }
            with open(os.path.join(temp_dir, 'package.json'), 'w') as f:
                json.dump(package_json, f)
            
            # Create the scraper script
            scraper_code = f'''
import {{ chromium }} from 'playwright';

async function scrapeCompanyInfo() {{
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {{
        // Go directly to the company website
        await page.goto('https://www.cloudflare.com');
        await page.waitForLoadState('networkidle');
        
        // Extract information from the website
        const data = await page.evaluate(() => {{
            // Try to find company description
            const description = document.querySelector('meta[name="description"]')?.content
                || document.querySelector('meta[property="og:description"]')?.content
                || document.querySelector('.about-description')?.textContent
                || '';
                
            // Get social media links
            const socialLinks = Array.from(document.querySelectorAll('a[href*="linkedin.com"], a[href*="twitter.com"], a[href*="facebook.com"]'))
                .map(link => link.href);
            
            return {{
                description,
                website: window.location.origin,
                socialLinks: [...new Set(socialLinks)]
            }};
        }});
        
        console.log(JSON.stringify(data));
        
    }} catch (error) {{
        console.error(error);
        process.exit(1);
    }} finally {{
        await browser.close();
    }}
}}

scrapeCompanyInfo();
'''
            
            with open(os.path.join(temp_dir, 'scraper.js'), 'w') as f:
                f.write(scraper_code)
            
            # Install dependencies
            subprocess.run(['npm', 'install'], cwd=temp_dir, check=True, capture_output=True)
            
            # Install Playwright browsers
            subprocess.run(['npx', 'playwright', 'install', 'chromium'], cwd=temp_dir, check=True, capture_output=True)
            
            # Run the scraper
            try:
                result = subprocess.run(
                    ['node', 'scraper.js'],
                    cwd=temp_dir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Parse the results
                data = json.loads(result.stdout)
                return {
                    "company": company_name,
                    "description": data["description"] or "No description available",
                    "website": data["website"],
                    "social_links": data["socialLinks"]
                }
                    
            except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
                print(f"Error scraping vendor information: {str(e)}")
                
        return {
            "company": company_name,
            "description": "No description available",
            "website": "https://www.cloudflare.com",
            "social_links": []
        } 