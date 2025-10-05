
# packages 
install.packages(c("ggplot2", "dplyr", "readr", "tidyverse"))  
library(ggplot2)
library(dplyr)
library(readr)

# data
df <- read_csv("all_raw.csv", show_col_types = FALSE)

# close price distribution

ggplot(df, aes(x = ClosePrice)) +
  geom_histogram(bins = 100, fill = "steelblue", color = "white") +
  scale_x_log10() +
  labs(title = "Distribution of List Price (log scale)", x = "List Price (log10)", y = "Count") +
  theme_minimal()

# living area

ggplot(df, aes(x = LivingArea)) +
  geom_histogram(bins = 100, fill = "darkgreen", color = "white") +
  scale_x_continuous(limits = c(0, 10000)) +
  labs(title = "Distribution of Living Area (sqft)", x = "Living Area (sqft)", y = "Count") +
  theme_minimal()

# price vs. area

ggplot(df, aes(x = LivingArea, y = ClosePrice)) +
  geom_point(alpha = 0.2, color = "darkred") +
  scale_x_continuous(limits = c(0, 10000)) +
  scale_y_log10() +
  labs(title = "List Price vs. Living Area", x = "Living Area (sqft)", y = "List Price (log10)") +
  theme_minimal()

# property type count

df %>%
  count(PropertyType, sort = TRUE) %>%
  slice_max(n, n = 10) %>%
  ggplot(aes(x = reorder(PropertyType, n), y = n)) +
  geom_col(fill = "purple") +
  coord_flip() +
  labs(title = "Top Property Types", x = "Property Type", y = "Number of Listings") +
  theme_minimal()
