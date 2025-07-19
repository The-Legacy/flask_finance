class TaxCalculator:
    """Calculate tax brackets and withholding estimates for US federal, state, and local taxes"""
    
    # 2024 Federal Tax Brackets (Single Filer)
    TAX_BRACKETS_SINGLE = [
        (11000, 0.10),
        (44725, 0.12),
        (95375, 0.22),
        (182050, 0.24),
        (231250, 0.32),
        (578125, 0.35),
        (float('inf'), 0.37)
    ]
    
    # Standard deduction for 2024
    STANDARD_DEDUCTION_SINGLE = 14600
    
    # Social Security and Medicare rates
    SOCIAL_SECURITY_RATE = 0.062  # 6.2%
    MEDICARE_RATE = 0.0145  # 1.45%
    SELF_EMPLOYMENT_TAX_RATE = 0.153  # 15.3% (employer + employee portion)
    
    # Social Security wage base limit for 2024
    SOCIAL_SECURITY_WAGE_BASE = 160200
    
    # State Tax Data (2024 rates - simplified)
    STATE_TAX_DATA = {
        'AL': {'rate': 0.05, 'name': 'Alabama', 'deduction': 2500},
        'AK': {'rate': 0.00, 'name': 'Alaska', 'deduction': 0},
        'AZ': {'rate': 0.025, 'name': 'Arizona', 'deduction': 13850},
        'AR': {'rate': 0.069, 'name': 'Arkansas', 'deduction': 2340},
        'CA': {'rate': 0.133, 'name': 'California', 'deduction': 5202},
        'CO': {'rate': 0.0455, 'name': 'Colorado', 'deduction': 14600},
        'CT': {'rate': 0.0699, 'name': 'Connecticut', 'deduction': 0},
        'DE': {'rate': 0.066, 'name': 'Delaware', 'deduction': 3250},
        'FL': {'rate': 0.00, 'name': 'Florida', 'deduction': 0},
        'GA': {'rate': 0.0575, 'name': 'Georgia', 'deduction': 4600},
        'HI': {'rate': 0.11, 'name': 'Hawaii', 'deduction': 2200},
        'ID': {'rate': 0.058, 'name': 'Idaho', 'deduction': 14600},
        'IL': {'rate': 0.0495, 'name': 'Illinois', 'deduction': 2775},
        'IN': {'rate': 0.0323, 'name': 'Indiana', 'deduction': 1000},
        'IA': {'rate': 0.0853, 'name': 'Iowa', 'deduction': 2210},
        'KS': {'rate': 0.057, 'name': 'Kansas', 'deduction': 3500},
        'KY': {'rate': 0.05, 'name': 'Kentucky', 'deduction': 2950},
        'LA': {'rate': 0.0425, 'name': 'Louisiana', 'deduction': 4500},
        'ME': {'rate': 0.0715, 'name': 'Maine', 'deduction': 14600},
        'MD': {'rate': 0.0575, 'name': 'Maryland', 'deduction': 2400},
        'MA': {'rate': 0.05, 'name': 'Massachusetts', 'deduction': 8000},
        'MI': {'rate': 0.0425, 'name': 'Michigan', 'deduction': 5000},
        'MN': {'rate': 0.0985, 'name': 'Minnesota', 'deduction': 14600},
        'MS': {'rate': 0.05, 'name': 'Mississippi', 'deduction': 2300},
        'MO': {'rate': 0.054, 'name': 'Missouri', 'deduction': 2150},
        'MT': {'rate': 0.0675, 'name': 'Montana', 'deduction': 5610},
        'NE': {'rate': 0.0684, 'name': 'Nebraska', 'deduction': 7700},
        'NV': {'rate': 0.00, 'name': 'Nevada', 'deduction': 0},
        'NH': {'rate': 0.00, 'name': 'New Hampshire', 'deduction': 0},
        'NJ': {'rate': 0.1075, 'name': 'New Jersey', 'deduction': 1000},
        'NM': {'rate': 0.059, 'name': 'New Mexico', 'deduction': 14600},
        'NY': {'rate': 0.109, 'name': 'New York', 'deduction': 8000},
        'NC': {'rate': 0.0475, 'name': 'North Carolina', 'deduction': 12750},
        'ND': {'rate': 0.0295, 'name': 'North Dakota', 'deduction': 14600},
        'OH': {'rate': 0.0399, 'name': 'Ohio', 'deduction': 2400},
        'OK': {'rate': 0.05, 'name': 'Oklahoma', 'deduction': 6350},
        'OR': {'rate': 0.099, 'name': 'Oregon', 'deduction': 2800},
        'PA': {'rate': 0.0307, 'name': 'Pennsylvania', 'deduction': 0},
        'RI': {'rate': 0.0599, 'name': 'Rhode Island', 'deduction': 9600},
        'SC': {'rate': 0.07, 'name': 'South Carolina', 'deduction': 12760},
        'SD': {'rate': 0.00, 'name': 'South Dakota', 'deduction': 0},
        'TN': {'rate': 0.00, 'name': 'Tennessee', 'deduction': 0},
        'TX': {'rate': 0.00, 'name': 'Texas', 'deduction': 0},
        'UT': {'rate': 0.0485, 'name': 'Utah', 'deduction': 14600},
        'VT': {'rate': 0.0875, 'name': 'Vermont', 'deduction': 7100},
        'VA': {'rate': 0.0575, 'name': 'Virginia', 'deduction': 4500},
        'WA': {'rate': 0.00, 'name': 'Washington', 'deduction': 0},
        'WV': {'rate': 0.065, 'name': 'West Virginia', 'deduction': 2000},
        'WI': {'rate': 0.0765, 'name': 'Wisconsin', 'deduction': 14070},
        'WY': {'rate': 0.00, 'name': 'Wyoming', 'deduction': 0},
        'DC': {'rate': 0.1075, 'name': 'Washington D.C.', 'deduction': 14600}
    }
    
    # Major cities with local income tax (simplified)
    LOCAL_TAX_DATA = {
        # New York State
        'NYC': {'rate': 0.03078, 'name': 'New York City', 'state': 'NY'},
        'YON': {'rate': 0.01477, 'name': 'Yonkers', 'state': 'NY'},
        
        # Pennsylvania - Many municipalities have local taxes
        'PHL': {'rate': 0.038712, 'name': 'Philadelphia', 'state': 'PA'},
        'PIT': {'rate': 0.03, 'name': 'Pittsburgh', 'state': 'PA'},
        'ALT': {'rate': 0.015, 'name': 'Altoona', 'state': 'PA'},
        'BET': {'rate': 0.0125, 'name': 'Bethlehem', 'state': 'PA'},
        'CHE': {'rate': 0.005, 'name': 'Chester', 'state': 'PA'},
        'ERI': {'rate': 0.0155, 'name': 'Erie', 'state': 'PA'},
        'HAR': {'rate': 0.0205, 'name': 'Harrisburg', 'state': 'PA'},
        'LAN_PA': {'rate': 0.0125, 'name': 'Lancaster', 'state': 'PA'},
        'REA': {'rate': 0.0155, 'name': 'Reading', 'state': 'PA'},
        'SCR': {'rate': 0.0325, 'name': 'Scranton', 'state': 'PA'},
        'WIL_PA': {'rate': 0.015, 'name': 'Wilkes-Barre', 'state': 'PA'},
        'YOR': {'rate': 0.0155, 'name': 'York', 'state': 'PA'},
        
        # Ohio - Many cities have local income taxes
        'CLE': {'rate': 0.025, 'name': 'Cleveland', 'state': 'OH'},
        'CIN': {'rate': 0.019, 'name': 'Cincinnati', 'state': 'OH'},
        'COL': {'rate': 0.025, 'name': 'Columbus', 'state': 'OH'},
        'TOL': {'rate': 0.0225, 'name': 'Toledo', 'state': 'OH'},
        'AKR': {'rate': 0.025, 'name': 'Akron', 'state': 'OH'},
        'DAY': {'rate': 0.0225, 'name': 'Dayton', 'state': 'OH'},
        'YOU': {'rate': 0.025, 'name': 'Youngstown', 'state': 'OH'},
        'CAN': {'rate': 0.015, 'name': 'Canton', 'state': 'OH'},
        'LOR': {'rate': 0.015, 'name': 'Lorain', 'state': 'OH'},
        'SPR': {'rate': 0.02, 'name': 'Springfield', 'state': 'OH'},
        'PAR': {'rate': 0.02, 'name': 'Parma', 'state': 'OH'},
        'ELY': {'rate': 0.015, 'name': 'Elyria', 'state': 'OH'},
        
        # Michigan
        'DET': {'rate': 0.024, 'name': 'Detroit', 'state': 'MI'},
        'GRA': {'rate': 0.013, 'name': 'Grand Rapids', 'state': 'MI'},
        'FLI': {'rate': 0.01, 'name': 'Flint', 'state': 'MI'},
        'LAN_MI': {'rate': 0.01, 'name': 'Lansing', 'state': 'MI'},
        'SAG': {'rate': 0.015, 'name': 'Saginaw', 'state': 'MI'},
        'PON': {'rate': 0.01, 'name': 'Pontiac', 'state': 'MI'},
        'BAY': {'rate': 0.01, 'name': 'Bay City', 'state': 'MI'},
        'JAC': {'rate': 0.01, 'name': 'Jackson', 'state': 'MI'},
        'KAL': {'rate': 0.01, 'name': 'Kalamazoo', 'state': 'MI'},
        'MUS': {'rate': 0.01, 'name': 'Muskegon', 'state': 'MI'},
        'BIG': {'rate': 0.01, 'name': 'Big Rapids', 'state': 'MI'},
        'ALB': {'rate': 0.01, 'name': 'Albion', 'state': 'MI'},
        
        # Missouri
        'KC': {'rate': 0.01, 'name': 'Kansas City', 'state': 'MO'},
        'STL': {'rate': 0.01, 'name': 'St. Louis', 'state': 'MO'},
        
        # Alabama
        'BIR': {'rate': 0.01, 'name': 'Birmingham', 'state': 'AL'},
        'GDS': {'rate': 0.005, 'name': 'Gadsden', 'state': 'AL'},
        
        # Kentucky
        'LOU': {'rate': 0.0045, 'name': 'Louisville', 'state': 'KY'},
        'LEX': {'rate': 0.0025, 'name': 'Lexington', 'state': 'KY'},
        
        # Indiana
        'EVA': {'rate': 0.0025, 'name': 'Evansville', 'state': 'IN'},
        'FWA': {'rate': 0.0025, 'name': 'Fort Wayne', 'state': 'IN'},
        
        # Maryland
        'BAL': {'rate': 0.0320, 'name': 'Baltimore', 'state': 'MD'},
        
        # District of Columbia
        'DC': {'rate': 0.0, 'name': 'Washington D.C. (No Additional Local Tax)', 'state': 'DC'},
        
        # Iowa (Some cities)
        'DSM': {'rate': 0.01, 'name': 'Des Moines', 'state': 'IA'},
        'DAV': {'rate': 0.01, 'name': 'Davenport', 'state': 'IA'},
        
        # Delaware (Wilmington)
        'WIL_DE': {'rate': 0.0125, 'name': 'Wilmington', 'state': 'DE'},
        
        # Arkansas (Some cities)
        'LIT': {'rate': 0.005, 'name': 'Little Rock', 'state': 'AR'},
        
        # Oregon (Portland Metro Area - Transit Tax)
        'POR': {'rate': 0.00746, 'name': 'Portland Metro (TriMet Tax)', 'state': 'OR'},
        
        # Major cities in no-local-tax states for reference
        'SF': {'rate': 0.0, 'name': 'San Francisco (No Local Income Tax)', 'state': 'CA'},
        'LA': {'rate': 0.0, 'name': 'Los Angeles (No Local Income Tax)', 'state': 'CA'},
        'SD': {'rate': 0.0, 'name': 'San Diego (No Local Income Tax)', 'state': 'CA'},
        'CHI': {'rate': 0.0, 'name': 'Chicago (No Local Income Tax)', 'state': 'IL'},
        'HOU': {'rate': 0.0, 'name': 'Houston (No State/Local Income Tax)', 'state': 'TX'},
        'DAL': {'rate': 0.0, 'name': 'Dallas (No State/Local Income Tax)', 'state': 'TX'},
        'PHX': {'rate': 0.0, 'name': 'Phoenix (No Local Income Tax)', 'state': 'AZ'},
        'ATL': {'rate': 0.0, 'name': 'Atlanta (No Local Income Tax)', 'state': 'GA'},
        'DEN': {'rate': 0.0, 'name': 'Denver (No Local Income Tax)', 'state': 'CO'},
        'SEA': {'rate': 0.0, 'name': 'Seattle (No State Income Tax)', 'state': 'WA'},
        'MIA': {'rate': 0.0, 'name': 'Miami (No State Income Tax)', 'state': 'FL'},
        'LAS': {'rate': 0.0, 'name': 'Las Vegas (No State Income Tax)', 'state': 'NV'},
        'BOS': {'rate': 0.0, 'name': 'Boston (No Local Income Tax)', 'state': 'MA'},
    }
    
    def calculate_state_tax(self, income, state_code):
        """Calculate state income tax"""
        if state_code not in self.STATE_TAX_DATA:
            return {'state_tax': 0, 'state_name': 'Unknown', 'taxable_income': income}
        
        state_info = self.STATE_TAX_DATA[state_code]
        state_deduction = state_info['deduction']
        state_rate = state_info['rate']
        
        # Calculate state taxable income
        state_taxable_income = max(0, income - state_deduction)
        
        # Most states use flat rate (simplified calculation)
        state_tax = state_taxable_income * state_rate
        
        return {
            'state_tax': state_tax,
            'state_name': state_info['name'],
            'state_rate': state_rate * 100,
            'state_deduction': state_deduction,
            'taxable_income': state_taxable_income
        }
    
    def calculate_local_tax(self, income, city_code=None):
        """Calculate local/city income tax"""
        if not city_code or city_code not in self.LOCAL_TAX_DATA:
            return {'local_tax': 0, 'city_name': None, 'local_rate': 0}
        
        city_info = self.LOCAL_TAX_DATA[city_code]
        local_rate = city_info['rate']
        
        # Most local taxes are flat rate on gross income (simplified)
        local_tax = income * local_rate
        
        return {
            'local_tax': local_tax,
            'city_name': city_info['name'],
            'local_rate': local_rate * 100
        }
    
    def get_state_list(self):
        """Get list of all states for dropdown"""
        return [{'code': code, 'name': data['name']} for code, data in sorted(self.STATE_TAX_DATA.items())]
    
    def get_cities_for_state(self, state_code):
        """Get list of cities with local taxes for a given state"""
        cities = []
        for city_code, city_data in self.LOCAL_TAX_DATA.items():
            if city_data['state'] == state_code:
                cities.append({'code': city_code, 'name': city_data['name']})
        return cities
        """Calculate federal income tax based on tax brackets"""
        if filing_status != 'single':
            # For simplicity, only implementing single filer brackets
            # In a full implementation, you'd have brackets for married filing jointly, etc.
            pass
        
        brackets = self.TAX_BRACKETS_SINGLE
        tax_owed = 0
        previous_bracket = 0
        
        for bracket_limit, rate in brackets:
            if taxable_income <= previous_bracket:
                break
                
            taxable_in_bracket = min(taxable_income, bracket_limit) - previous_bracket
            tax_owed += taxable_in_bracket * rate
            previous_bracket = bracket_limit
            
            if taxable_income <= bracket_limit:
                break
        
        return tax_owed
    
    def calculate_payroll_taxes(self, gross_income):
        """Calculate Social Security and Medicare taxes"""
        # Social Security tax (capped at wage base)
        ss_wages = min(gross_income, self.SOCIAL_SECURITY_WAGE_BASE)
        social_security_tax = ss_wages * self.SOCIAL_SECURITY_RATE
        
        # Medicare tax (no cap)
        medicare_tax = gross_income * self.MEDICARE_RATE
        
        # Additional Medicare tax for high earners (0.9% on income over $200k)
        additional_medicare = 0
        if gross_income > 200000:
            additional_medicare = (gross_income - 200000) * 0.009
        
        return {
            'social_security': social_security_tax,
            'medicare': medicare_tax + additional_medicare,
            'total_payroll': social_security_tax + medicare_tax + additional_medicare
        }
    
    def calculate_self_employment_tax(self, net_earnings):
        """Calculate self-employment tax for 1099 contractors"""
        # 92.35% of net earnings subject to self-employment tax
        se_income = net_earnings * 0.9235
        
        # Social Security portion (capped)
        ss_wages = min(se_income, self.SOCIAL_SECURITY_WAGE_BASE)
        ss_tax = ss_wages * (self.SOCIAL_SECURITY_RATE * 2)  # Both employer and employee portions
        
        # Medicare portion (no cap)
        medicare_tax = se_income * (self.MEDICARE_RATE * 2)  # Both employer and employee portions
        
        # Additional Medicare tax for high earners
        additional_medicare = 0
        if se_income > 200000:
            additional_medicare = (se_income - 200000) * 0.009
        
        total_se_tax = ss_tax + medicare_tax + additional_medicare
        
        return {
            'self_employment_tax': total_se_tax,
            'deductible_portion': total_se_tax * 0.5,  # Half is deductible
            'social_security_portion': ss_tax,
            'medicare_portion': medicare_tax + additional_medicare
        }
    
    def calculate_taxes(self, annual_income, employment_type, filing_status='single', state_code=None, city_code=None):
        """Main method to calculate all taxes and withholding estimates"""
        result = {
            'annual_income': annual_income,
            'employment_type': employment_type,
            'filing_status': filing_status,
            'state_code': state_code,
            'city_code': city_code
        }
        
        # Calculate state taxes
        state_tax_info = self.calculate_state_tax(annual_income, state_code) if state_code else {
            'state_tax': 0, 'state_name': None, 'state_rate': 0, 'state_deduction': 0, 'taxable_income': annual_income
        }
        
        # Calculate local taxes
        local_tax_info = self.calculate_local_tax(annual_income, city_code) if city_code else {
            'local_tax': 0, 'city_name': None, 'local_rate': 0
        }
        
        if employment_type == '1099':
            # Self-employed / Contractor
            se_tax_info = self.calculate_self_employment_tax(annual_income)
            
            # Adjusted gross income (subtract half of SE tax)
            agi = annual_income - se_tax_info['deductible_portion']
            taxable_income = max(0, agi - self.STANDARD_DEDUCTION_SINGLE)
            
            federal_income_tax = self.calculate_federal_income_tax(taxable_income, filing_status)
            
            # Total tax calculation
            total_federal = se_tax_info['self_employment_tax'] + federal_income_tax
            total_state = state_tax_info['state_tax']
            total_local = local_tax_info['local_tax']
            total_all_taxes = total_federal + total_state + total_local
            
            result.update({
                'self_employment_tax': se_tax_info['self_employment_tax'],
                'federal_income_tax': federal_income_tax,
                'total_federal_tax': total_federal,
                'state_tax_info': state_tax_info,
                'local_tax_info': local_tax_info,
                'total_tax_owed': total_all_taxes,
                'adjusted_gross_income': agi,
                'taxable_income': taxable_income,
                'effective_tax_rate': (total_all_taxes / annual_income) * 100,
                'quarterly_payment_estimate': total_all_taxes / 4,
                'se_tax_breakdown': se_tax_info
            })
            
        elif employment_type == 'w2':
            # W-2 Employee
            payroll_taxes = self.calculate_payroll_taxes(annual_income)
            taxable_income = max(0, annual_income - self.STANDARD_DEDUCTION_SINGLE)
            federal_income_tax = self.calculate_federal_income_tax(taxable_income, filing_status)
            
            # Total tax calculation
            total_federal = payroll_taxes['total_payroll'] + federal_income_tax
            total_state = state_tax_info['state_tax']
            total_local = local_tax_info['local_tax']
            total_all_taxes = total_federal + total_state + total_local
            
            result.update({
                'payroll_taxes': payroll_taxes,
                'federal_income_tax': federal_income_tax,
                'total_federal_tax': total_federal,
                'state_tax_info': state_tax_info,
                'local_tax_info': local_tax_info,
                'total_tax_owed': total_all_taxes,
                'taxable_income': taxable_income,
                'effective_tax_rate': (total_all_taxes / annual_income) * 100,
                'monthly_withholding_estimate': total_all_taxes / 12
            })
        
        # Determine tax bracket
        marginal_rate = self.get_marginal_tax_rate(annual_income)
        result['marginal_tax_rate'] = marginal_rate * 100
        
        # Add breakdown for display
        result['tax_breakdown'] = {
            'federal': total_federal,
            'state': total_state,
            'local': total_local,
            'total': total_all_taxes
        }
        
        return result
    
    def calculate_federal_income_tax(self, taxable_income, filing_status='single'):
        """Calculate federal income tax based on tax brackets"""
        if filing_status != 'single':
            # For simplicity, only implementing single filer brackets
            # In a full implementation, you'd have brackets for married filing jointly, etc.
            raise NotImplementedError("Only single filing status is currently supported")
        
        brackets = self.TAX_BRACKETS_SINGLE
        tax_owed = 0
        previous_bracket = 0
        
        for bracket_limit, rate in brackets:
            if taxable_income <= previous_bracket:
                break
                
            taxable_in_bracket = min(taxable_income, bracket_limit) - previous_bracket
            tax_owed += taxable_in_bracket * rate
            previous_bracket = bracket_limit
            
            if taxable_income <= bracket_limit:
                break
        
        return tax_owed
    
    def get_marginal_tax_rate(self, income):
        """Get the marginal tax rate for a given income level"""
        previous_bracket = 0
        
        for bracket_limit, rate in self.TAX_BRACKETS_SINGLE:
            if income <= bracket_limit:
                return rate
            previous_bracket = bracket_limit
        
        return self.TAX_BRACKETS_SINGLE[-1][1]  # Highest bracket
