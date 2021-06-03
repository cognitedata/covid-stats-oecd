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


def color_tests(val):
    color = "white"
    try:
        val = float(val[:-1])
        if val >= 4:
            color = "lightcoral"
        elif val < 4:
            color = "limegreen"
    except:
        color = "white"
    return "background-color: %s" % color


def color_cases(val):
    color = "white"
    try:
        val = float(val)
        if val >= 150:
            color = "lightcoral"
        elif val >= 25:
            color = "gold"
        elif val < 25:
            color = "limegreen"
    except:
        color = "white"
    return "background-color: %s" % color


def display_rules(country, value_latest_test, value_latest_cases):
    if (value_latest_test < 4) & (value_latest_cases < 25):
        return st.write(
            "**" + country + "**:" + " No quarantine required. :sun_with_face:"
        )
    elif (value_latest_test < 4) & (value_latest_cases < 150):
        return st.write(
            "**" + country + "**:" + " Quarantine at home required. :house:"
        )
    else:
        return st.write(
            "**" + country + "**:" + " Quarantine at hotel required. :hotel:"
        )


try:
    df_tests = get_OECD_data("testing")
    df_cases = get_OECD_data("nationalcasedeath")

    countries = st.multiselect(
        "Choose country", sorted(list(set(df_tests.index))), ["Germany"]
    )

    if not countries:
        st.error("Please select at least one country.")
    else:
        data_tests = df_tests.loc[countries].reset_index()
        data_cases = df_cases.loc[countries].reset_index()

        data_tests = data_tests[data_tests.level == "national"]
        data_cases = data_cases[data_cases.indicator == "cases"]

        data_tests["year_week"] = data_tests["year_week"].str.replace("W", "")
        data_tests["Date"] = pd.to_datetime(
            data_tests.year_week + "-0", format="%Y-%W-%w"
        )

        data_cases["Date"] = pd.to_datetime(
            data_cases.year_week + "-0", format="%Y-%W-%w"
        )
        st.write("### Quarantine Regulations for Immigration to Norway")
        for country in countries:
            data_tests_fil = data_tests[data_tests.country == country]
            data_cases_fil = data_cases[data_cases.country == country]

            index_lates_test = data_tests_fil["Date"].idxmax()
            index_lates_cases = data_cases_fil["Date"].idxmax()

            value_latest_test = data_tests_fil.loc[index_lates_test, "positivity_rate"]
            value_latest_cases = data_cases_fil.loc[index_lates_cases, "rate_14_day"]

            display_rules(country, value_latest_test, value_latest_cases)
        st.write(
            "*Disclaimer: Quarantine regulations are subject to change. Please verify with latest [FHI regulations](https://www.fhi.no/publ/2020/covid-19-faglige-notater-som-grunnlag-for-nasjonale-beslutninger/#tallgrunnlag-for-innreisekarantene).* "
        )
        # Tests
        columns = [
            "country",
            "year_week",
            "new_cases",
            "tests_done",
            "population",
            "positivity_rate_p",
        ]

        data_tests["population"] = data_tests["population"].astype("int")

        data_tests["positivity_rate_p"] = pd.Series(
            ["{0:.2f}%".format(val) for val in data_tests["positivity_rate"]],
            index=data_tests.index,
        )

        st.write(
            "### COVID-19 Testing",
            data_tests[columns]
            .sort_values("year_week", axis=0, ascending=False)
            .reset_index(drop=True)
            .style.applymap(
                color_tests, subset=pd.IndexSlice[:, ["positivity_rate_p"]]
            ),
        )

        st.text("")

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

        # Cases

        columns_cases = [
            "country",
            "year_week",
            "indicator",
            "population",
            "weekly_count",
            "rate_14_day",
        ]

        st.write(
            "### 14-day notification rate of COVID-19 cases (per 100 000 population)",
            data_cases[columns_cases]
            .sort_values("year_week", axis=0, ascending=False)
            .reset_index(drop=True)
            .style.applymap(color_cases, subset=pd.IndexSlice[:, ["rate_14_day"]]),
        )

        st.text("")

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

    st.write(
        "Sources: [OECD](https://www.ecdc.europa.eu/en/covid-19/data), [FHI](https://www.fhi.no/publ/2020/covid-19-faglige-notater-som-grunnlag-for-nasjonale-beslutninger/#tallgrunnlag-for-innreisekarantene)"
    )


except URLError as e:
    st.error(
        """
        **This app requires internet access.**

        Connection error: %s
    """
        % e.reason
    )
