import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Titel und Upload
st.title("Flowchart Generator aus CSV")

uploaded_file = st.file_uploader("Lade deine CSV-Datei hoch", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Sicherheitshalber prüfen, ob die nötigen Spalten vorhanden sind
    required_columns = {"Schritte", "Prozesse", "Verantwortung"}
    if not required_columns.issubset(df.columns):
        st.error(f"CSV muss die Spalten {required_columns} enthalten.")
    else:
        st.success("CSV erfolgreich geladen!")

        # Verantwortungsbereiche (Swimlanes)
        responsibilities = df['Verantwortung'].unique()
        responsibility_to_y = {resp: i for i, resp in enumerate(responsibilities[::-1])}

        fig = go.Figure()

        # Swimlanes zeichnen
        lane_height = 1
        for resp, y_index in responsibility_to_y.items():
            fig.add_shape(
                type="rect",
                x0=0, x1=1, y0=y_index * lane_height, y1=(y_index + 1) * lane_height,
                line=dict(width=0),
                fillcolor=f"rgba({100 + y_index*50}, {150 + y_index*30}, 255, 0.2)",
                layer="below"
            )
            fig.add_annotation(
                x=-0.02, y=(y_index + 0.5) * lane_height,
                text=resp,
                showarrow=False,
                xanchor="right",
                font=dict(size=14)
            )

        # Prozesse als Bubbles platzieren
        node_positions = {}
        step_counter = 0
        total_steps = len(df)

        for idx, row in df.iterrows():
            step = row['Schritte']
            process = row['Prozesse']
            responsibility = row['Verantwortung']

            x = step_counter / (total_steps-1) if total_steps > 1 else 0.5
            y = responsibility_to_y[responsibility] * lane_height + lane_height/2
            node_positions[step] = (x, y)

            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(size=40, color="lightblue", line=dict(width=2, color="blue")),
                text=[process],
                textposition="middle center",
                hoverinfo="text"
            ))
            step_counter += 1

        # Pfeile zwischen den Schritten zeichnen
        steps = df['Schritte'].tolist()
        for i in range(len(steps) - 1):
            x0, y0 = node_positions[steps[i]]
            x1, y1 = node_positions[steps[i+1]]
            fig.add_annotation(
                x=x1, y=y1,
                ax=x0, ay=y0,
                xref='x', yref='y',
                axref='x', ayref='y',
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="black"
            )

        fig.update_layout(
            showlegend=False,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(visible=False, range=[-0.2,1.2]),
            yaxis=dict(visible=False, range=[-0.5, len(responsibilities)*lane_height]),
            height=300 + 100 * len(responsibilities)
        )

        st.plotly_chart(fig, use_container_width=True)
