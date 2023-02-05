async function populate(){
    const requestURL = './MyRealT_PortfolioOffline.json';
    const request = new Request(requestURL);
    const response = await fetch(request);
    const myPortfolio = await response.json();

    populateProperties(myPortfolio.data);
}

function populateProperties(jsonObj) {
    const portfolio = document.querySelector('portfolio');
    const properties = jsonObj;
    console.log(properties);

    for (const property in properties) {
        const myProperty = document.createElement('property');
        myProperty.classList.add('property-layout');
        const name = document.createElement('h2');
        const tokenAmount = document.createElement('p');
        const currentValuation = document.createElement('p');
        const currentRentedUnitP = document.createElement('p');
        const currentNetRentP = document.createElement('p');

        name.textContent = properties[property].Shortname;
        tokenAmount.textContent = 'Token owned: ' + properties[property].CurrentBalance.toFixed(5);
        currentValuation.textContent = 'Current value: ' + properties[property].CurrentValue.toFixed(2) + ' (/w ' + properties[property].InvestValue + ' invested)';
        currentRentedUnitP.textContent = 'Rented at ' + properties[property].CurrentRentedUnitsP;
        currentNetRentP.textContent = 'Current net rent ratio is ' + properties[property].CurrentNetRentP;

        myProperty.appendChild(name);
        myProperty.appendChild(tokenAmount);
        myProperty.appendChild(currentValuation);
        myProperty.appendChild(currentRentedUnitP);
        myProperty.appendChild(currentNetRentP);

        portfolio.appendChild(myProperty);
    };
}

populate();