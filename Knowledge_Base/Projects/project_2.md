# COVID-19 Vaccination Analysis Project - Comprehensive RAG Documentation

## Project Metadata
- **Project Title**: COVID-19 Vaccination Rates and Health Outcomes Analysis
- **Institution**: University of Toledo Data Science-I Course
- **Student**: Hoang Nhat Duy Le
- **Instructor**: David Lilley, PhD
- **Completion Date**: December 12, 2021
- **Assignment**: Final Project (Due: December 14, 2021)
- **Repository**: CovidVaccineProject (Owner: hoangnhatduyle)
- **Branch**: master

## Research Question
**Primary Question**: Whether or not COVID-19 vaccination rates are associated with fewer cases and deaths (excess mortality)?

## Project Structure and Files

### Main Analysis Files
- **FinalProject.sas**: Primary SAS analysis script (204 lines)
- **Final Project Report.docx**: Project documentation and report
- **Dataset/**: Primary data directory containing analysis datasets
- **DS Project/**: Secondary directory with additional data and submitted versions

### Data Sources and Files

#### Primary COVID-19 Data
1. **owid_covid_data_final_project_Nov42021.csv** (130,815 records)
   - Source: Our World in Data COVID-19 dataset
   - Contains 58 variables including:
     - Geographic: iso_code, continent, location, date
     - Case metrics: total_cases, new_cases, new_cases_per_million
     - Death metrics: total_deaths, new_deaths
     - Vaccination metrics: people_fully_vaccinated, people_fully_vacc_per_hundred
     - Health system: icu_patients, hosp_patients
     - Testing: total_tests, positive_rate
     - Policy: stringency_index
     - Demographics: population, median_age, aged_65_older

2. **Excess_Mortality.csv** (6,813 records)
   - Monthly excess mortality data by country
   - Variables: location, date, year, month, excess_mortality
   - Time series data from 2020-2021

#### Supporting Socioeconomic Datasets

3. **Economic.csv** (219 countries)
   - Variables: iso_code, location, gdp_percap, inflat_rate_yearly, unempl_rate, labor_force_rate, economic_year
   - Economic indicators for 2020

4. **Health.csv** (268 records)
   - Variables: iso_code, location, health_year, physician, Domestic_Health_Exp_GDP, Domestic_Health_Exp_Pcapita, Curr_Health_Exp_GDP, Curr_Health_Exp_Pcapita, Hospital_Beds
   - Health system expenditure and infrastructure data (2018)

5. **Population.csv** (436 records)
   - Variables: location, iso_code, population_year, Death_Rate_per_1000, Population__total, Population__male, Population__female, Ages_over_64, Ages_15_to_64, Ages_00_to_14
   - Demographic data for 2019-2020

6. **Unemploy.csv** (250 records)
   - Unemployment rate data by country

## Data Processing Methodology

### Data Import Process
- **Custom SAS Macro**: `%import(fileName, fileExtension, fileOutput, row)`
- **Function**: Imports CSV files with specified guessing rows for data type inference
- **File Path**: Uses local directory "C:\Users\hle4\Downloads\"

### Data Cleaning and Filtering Steps

#### Temporal Filtering
- **Time Period**: September-October 2021 only
- **Rationale**: Focus on period with substantial vaccination coverage
- **Filter Logic**: `where (month = 9 or month = 10)` and `if year ne 2021 then delete`

#### Data Quality Controls
1. **Vaccination Data**: Remove entries where `people_fully_vacc_per_hundred` is missing or ≤ 0
2. **Case Data**: Remove entries where `new_cases_per_million` is missing or ≤ 0
3. **Geographic Filtering**: Exclude non-country entities with OWID codes (`if find(iso_code,"OWID") then delete`)
4. **Location Standardization**: Convert location names to uppercase

#### Data Aggregation Process
- **Grouping**: By iso_code (country level)
- **Method**: Calculate averages across September-October 2021 period
- **Key Aggregated Variables**:
  - `avg_new_cases_per_mil`: Average new cases per million
  - `avg_people_fully_vacc`: Average vaccination rate
  - `avg_excess_mortality`: Average excess mortality

### Data Integration
- **Primary Dataset**: COVID-19 data with excess mortality
- **Supporting Data**: Economic, Health, Population, Unemployment datasets
- **Join Key**: iso_code (ISO country codes)
- **Join Type**: Inner join ensuring all datasets contribute data

## Variables in Final Dataset

### Dependent Variables (Outcomes)
1. **avg_new_cases_per_mil**: Average new COVID-19 cases per million population
2. **avg_excess_mortality**: Average excess mortality percentage

### Independent Variables (Predictors)

#### Vaccination Variable
- **avg_people_fully_vacc**: Average percentage of population fully vaccinated

#### Economic Variables
- **gdp_percap**: GDP per capita (2020)
- **unemployment_rate**: Unemployment rate (2020)

#### Health System Variables
- **domestic_health_exp**: Domestic health expenditure as % of GDP (2018)
- **curr_health_exp**: Current health expenditure as % of GDP (2018)

#### Demographic Variables
- **avg_total_population**: Average total population
- **avg_ages_over_64**: Average population over 64 years old

#### Geographic Variables
- **iso_code**: ISO country code (primary key)
- **continent**: Continental grouping
- **location**: Country name (uppercase)

## Statistical Analysis Methods

### Correlation Analysis
- **Procedure**: `PROC CORR`
- **Variables Analyzed**: All continuous variables in final dataset
- **Purpose**: Examine bivariate relationships between vaccination rates and health outcomes

### Multiple Regression Analysis
- **Procedure**: `PROC REG`
- **Models**: Two separate regression models

#### Model 1: New Cases Analysis
```sas
model avg_new_cases_per_mil = avg_people_fully_vacc gdp_percap domestic_health_exp 
      curr_health_exp avg_total_population avg_ages_over_64 unemployment_rate;
```

#### Model 2: Excess Mortality Analysis
```sas
model avg_excess_mortality = avg_people_fully_vacc gdp_percap domestic_health_exp 
      curr_health_exp avg_total_population avg_ages_over_64 unemployment_rate;
```

## Technical Implementation Details

### Programming Language
- **Primary**: SAS
- **Script Length**: 204 lines of code
- **Platform**: Windows environment

### Data Processing Flow
1. **Import Phase**: Load all CSV datasets using custom macro
2. **Temporal Processing**: Create year and month variables from dates
3. **Data Cleaning**: Apply quality filters and exclusions
4. **Aggregation**: Calculate country-level averages for Sep-Oct 2021
5. **Integration**: Merge COVID data with socioeconomic datasets
6. **Variable Transformation**: Convert string variables to numeric
7. **Analysis**: Run correlation and regression analyses
8. **Export**: Output final dataset to Excel format

### Key SAS Procedures Used
- **PROC IMPORT**: Data ingestion
- **DATA steps**: Data manipulation and cleaning
- **PROC SORT**: Data ordering for merges
- **PROC CORR**: Correlation analysis
- **PROC REG**: Regression modeling
- **PROC EXPORT**: Results export

## Research Design Characteristics

### Study Type
- **Design**: Cross-sectional ecological study
- **Unit of Analysis**: Country-level data
- **Time Frame**: September-October 2021 snapshot

### Geographic Scope
- **Coverage**: Global (countries with available data)
- **Exclusions**: Non-country entities, territories with OWID codes
- **Sample Size**: Variable by analysis (depends on data availability)

### Temporal Considerations
- **COVID Data**: Daily data aggregated to country-level averages for Sep-Oct 2021
- **Economic Data**: 2020 annual figures
- **Health Expenditure**: 2018 data (most recent available)
- **Population Data**: 2019-2020 figures

## Data Quality and Limitations

### Strengths
- **Comprehensive Coverage**: Multi-dimensional dataset with health, economic, and demographic variables
- **Standardized Metrics**: Use of per-capita and percentage measures for comparability
- **Quality Controls**: Explicit filtering for missing and invalid data
- **Recent Data**: Focus on 2021 when vaccinations were widely available

### Potential Limitations
- **Temporal Misalignment**: Different reference years for various datasets
- **Ecological Fallacy**: Country-level analysis may not reflect individual-level relationships
- **Missing Data**: Countries with incomplete vaccination or health data excluded
- **Confounding Variables**: Multiple factors influence COVID outcomes beyond vaccination

## Output and Results

### Final Dataset Export
- **Format**: Excel file ("FinalDataset")
- **Content**: Merged and processed country-level data ready for analysis
- **Variables**: All key predictors and outcomes for statistical modeling

### Analysis Components
1. **Descriptive Statistics**: Variable distributions and summary measures
2. **Correlation Matrix**: Bivariate relationships between all variables
3. **Regression Results**: Two models examining vaccination effects on health outcomes

## File Structure Summary
```
CovidVaccineProject/
├── FinalProject.sas                 # Main analysis script
├── Final Project Report.docx        # Project documentation
├── Dataset/                         # Primary data directory
│   ├── owid_covid_data_final_project_Nov42021.csv
│   ├── Excess_Mortality.csv
│   ├── Economic.csv
│   ├── Health.csv
│   ├── Population.csv
│   └── Unemploy.csv
└── DS Project/                      # Additional data and versions
    ├── Submitted/                   # Final submitted versions
    └── Data_2018-2020/             # Historical data files
```

## Usage Notes for RAG Systems

### Key Search Terms
- COVID-19 vaccination effectiveness
- Excess mortality analysis
- Country-level epidemiological study
- Vaccination rates and health outcomes
- Cross-sectional ecological study
- SAS statistical analysis
- Public health data integration

### Primary Research Applications
- Understanding vaccination program effectiveness
- Country-level health policy analysis
- Epidemiological surveillance methodology
- Multi-source health data integration
- Statistical modeling of public health outcomes

### Methodological Contributions
- Data cleaning and quality control procedures
- Multi-dataset integration techniques
- Temporal aggregation methods for epidemiological data
- Cross-sectional study design for vaccination effectiveness

This documentation provides comprehensive context for retrieval-augmented generation systems to understand and utilize information from this COVID-19 vaccination analysis project.