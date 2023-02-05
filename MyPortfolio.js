async function populate(){
    const requestURL = './MyRealT_PortfolioOffline.json';
    const request = new Request(requestURL);
    const response = await fetch(request);
    const myPortfolio = await response.json();

    populateProperties(myPortfolio.data);
}

function populateProperties(jsonObj) {
    const portfolio = document.getElementById('portfolio');
    const properties = jsonObj;

    for (const property in properties) {
        const myProperty = document.createElement('tr');
        const name = document.createElement('td');
        const tokenAmount = document.createElement('td');
        const currentValuation = document.createElement('td');
        const investedValue = document.createElement('td');
        const currentRentedUnitP = document.createElement('td');
        const currentNetRentP = document.createElement('td');

        name.textContent = properties[property].Shortname;
        tokenAmount.textContent = properties[property].CurrentBalance.toFixed(5);
        currentValuation.textContent = properties[property].CurrentValue.toFixed(2);
        if (properties[property].CurrentValue.toFixed(2) < properties[property].InvestValue.toFixed(2)) {
             currentValuation.style.backgroundColor = "red";
        } else if (properties[property].CurrentValue.toFixed(2) > properties[property].InvestValue.toFixed(2)){
            currentValuation.style.backgroundColor = "green";
        }
        investedValue.textContent = properties[property].InvestValue.toFixed(2);
        currentRentedUnitP.textContent = (/\d+ ?/).exec(properties[property].CurrentRentedUnitsP) + '%';
        if ((/\d+ ?/).exec(properties[property].CurrentRentedUnitsP) < 100) {
             currentRentedUnitP.style.backgroundColor = "red";
        }
        currentNetRentP.textContent = properties[property].CurrentNetRentP;

        myProperty.appendChild(name);
        myProperty.appendChild(tokenAmount);
        myProperty.appendChild(currentValuation);
        myProperty.appendChild(investedValue);
        myProperty.appendChild(currentRentedUnitP);
        myProperty.appendChild(currentNetRentP);

        portfolio.appendChild(myProperty);
    };
}

populate();