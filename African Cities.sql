Select Name From City Where CountryCode In (
    Select Code From Country Where Continent = 'Africa'
);