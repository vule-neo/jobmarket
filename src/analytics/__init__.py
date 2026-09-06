"""Analiza trzista - racunanje odvojeno od prikaza.

Svaka funkcija vraca DataFrame i nista ne crta i ne printa. Tako se isti
kod koristi i u notebooku i kasnije u FastAPI endpointu, gdje se rezultat
pretvori u JSON preko .to_dict("records") i posalje Angularu.
"""
