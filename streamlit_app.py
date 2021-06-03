import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError


st.title("Current COVID-19 Statistics Europe")


@st.cache
def get_OECD_data(category):
    OECD_URL = "https://opendata.ecdc.europa.eu/covid19/"
    df = pd.read_csv(OECD_URL + category + "/csv")
    return df.set_index("country")


try:
    df_tests = get_OECD_data("testing")
    countries = st.multiselect(
        "Choose country", sorted(list(set(df_tests.index))), ["Germany"]
    )

    if not countries:
        st.error("Please select at least one country.")
    else:
        data_tests = df_tests.loc[countries]
        columns = [
            "year_week",
            "new_cases",
            "tests_done",
            "population",
            "positivity_rate_perc",
        ]

        data_tests = data_tests[data_tests.level == "national"]
        data_tests["year_week"] = data_tests["year_week"].str.replace("W", "")

        data_tests["positivity_rate_perc"] = pd.Series(
            ["{0:.2f}%".format(val) for val in data_tests["positivity_rate"]],
            index=data_tests.index,
        )

        st.write(
            "### COVID-19 Testing",
            data_tests[columns].sort_values("year_week", axis=0, ascending=False),
        )

        st.text("")

        data_tests["Date"] = pd.to_datetime(
            data_tests.year_week + "-0", format="%Y-%W-%w"
        )
        data_tests["positivity_rate"] = data_tests["positivity_rate"] / 100

        data_tests = data_tests.reset_index()
        data_tests = data_tests.rename(
            columns={
                "index": "Date",
                "positivity_rate": "Positivity rate",
                "country": "Country",
            }
        )
        chart = (
            alt.Chart(data_tests)
            .mark_area(opacity=0.3)
            .encode(
                x="Date:T",
                y=alt.Y("Positivity rate:Q", stack=None, axis=alt.Axis(format=".0%")),
                color="Country:N",
                tooltip=[
                    "Date:T",
                    "Country:N",
                    alt.Tooltip("Positivity rate:Q", format=".2%"),
                ],
            )
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        df_cases = get_OECD_data("nationalcasedeath")

        data_cases = df_cases.loc[countries]
        columns = [
            "year_week",
            "indicator",
            "population",
            "weekly_count",
            "rate_14_day",
        ]
        data_cases = data_cases[data_cases.indicator == "cases"]

        st.write(
            "### 14-day notification rate of COVID-19 cases (per 100 000 population)",
            data_cases[columns].sort_values("year_week", axis=0, ascending=False),
        )

        st.text("")

        data_cases["Date"] = pd.to_datetime(
            data_cases.year_week + "-0", format="%Y-%W-%w"
        )

        data_cases = data_cases.reset_index()
        data_cases = data_cases.rename(
            columns={
                "index": "Date",
                "rate_14_day": "Number of Cases",
                "country": "Country",
            }
        )
        chart_cases = (
            alt.Chart(data_cases)
            .mark_area(opacity=0.3)
            .encode(
                x="Date:T",
                y=alt.Y("Number of Cases:Q", stack=None),
                color="Country:N",
                tooltip=[
                    "Date:T",
                    "Country:N",
                    "Number of Cases:Q",
                ],
            )
            .interactive()
        )
        st.altair_chart(chart_cases, use_container_width=True)

    st.write("[Source: OECD](https://www.ecdc.europa.eu/en/covid-19/data)")


except URLError as e:
    st.error(
        """
        **This app requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
