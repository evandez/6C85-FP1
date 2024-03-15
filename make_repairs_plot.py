import matplotlib.pyplot as plt
import pandas as pd

boston_zip_neighborhood = {
    "02108": "Beacon Hill",
    "02109": "North End",
    "02110": "Financial District",
    "02111": "Chinatown",
    "02113": "North End",
    "02114": "West End",
    "02115": "Fenway/Kenmore",
    "02116": "Back Bay",
    "02118": "South End",
    "02119": "Roxbury",
    "02120": "Mission Hill",
    "02121": "Dorchester",
    "02122": "Dorchester",
    "02124": "Dorchester",
    "02125": "Dorchester",
    "02126": "Mattapan",
    "02127": "South Boston",
    "02128": "East Boston",
    "02129": "Charlestown",
    "02130": "Jamaica Plain",
    "02131": "Roslindale",
    "02132": "West Roxbury",
    "02134": "Allston",
    "02135": "Brighton",
    "02136": "Hyde Park",
    # "02163": "Harvard University",
    "02210": "Seaport District",
    "02215": "Fenway/Kenmore",
}

# Load the CSV file into a pandas DataFrame
permits_df = pd.read_csv("data/boston_permits.csv", dtype={"zip": str})
permits_df["neighborhood"] = permits_df["zip"].map(boston_zip_neighborhood)
permits_df = permits_df[
    permits_df["occupancytype"].isin(
        {
            "1-2FAM",
            # "Comm",
            "Multi",
            "1-3FAM",
            # "Mixed",
            # "Other",
            "1-4FAM",
            "1Unit",
            # "VacLd",
            "7More",
            "1-7FAM",
            "3unit",
            "2unit",
            "4unit",
            "6unit",
            "5unit",
            "7unit",
        }
    )
]

sales_df = pd.read_csv("data/boston_residential_sales.csv", dtype={"zip": str})
sales_df["zip"] = sales_df["zip"].map(lambda x: f"0{x}")
sales_df["neighborhood"] = sales_df["zip"].map(boston_zip_neighborhood)

flipped_properties = sales_df[
    (sales_df["flip_ind"] == 1) & (sales_df["flip_term"] == "Long-term")
]

flipped_properties_by_neighborhood = (
    flipped_properties.groupby("neighborhood").size().reset_index(name="flipped_count")
)

# Filter data frame to only contain permits whose work includes "repairs"
merge_keywords = {
    "renovation": "(renovation|upgrade)",
    "maintenance": "(maint|repair|fix|service)",
}

merged_df = flipped_properties_by_neighborhood
for key, keyword in merge_keywords.items():
    filtered_df = permits_df[
        permits_df["description"].str.contains(
            keyword, case=False, na=False, regex=True
        )
        & permits_df["neighborhood"].notnull()
    ]
    merged_df = pd.merge(
        merged_df,
        filtered_df.groupby("neighborhood").size().reset_index(name=f"{key}_count"),
        on="neighborhood",
        how="outer",
    ).fillna(0)

merged_df = merged_df.sort_values("flipped_count", ascending=False)

# Create a bar plot of the number of permits by zip code
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot the number of flipped properties as bars
flipped_bars = ax1.bar(
    merged_df["neighborhood"],
    merged_df["flipped_count"],
    color="blue",
    alpha=0.7,
    label="Flipped Properties",
)
ax1.set_xlabel("Neighborhood")
ax1.set_ylabel("Number of Flipped Properties")
ax1.set_xticklabels(merged_df["neighborhood"], rotation=45, ha="right")

elements = list(flipped_bars)

# Create a second y-axis for repair permit counts
ax2 = ax1.twinx()
for i, (key, keyword) in enumerate(merge_keywords.items()):
    points = ax2.plot(
        merged_df["neighborhood"],
        merged_df[f"{key}_count"],
        marker="o",
        color=["red", "orange"][i],
        label=f"{key.capitalize()} Permits",
    )
    elements += points

ax1.legend(loc="upper left")
ax2.legend(loc="upper right")

ax2.set_ylabel("Number of Permits")
plt.title("Number of Flipped Properties and Permits by Neighborhood")
plt.tight_layout()
plt.show()
