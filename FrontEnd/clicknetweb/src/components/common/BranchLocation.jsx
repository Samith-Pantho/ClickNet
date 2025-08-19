import React, { useState, useEffect, useContext } from "react";
import { useNavigate } from 'react-router-dom';
import {MapContainer, TileLayer, Marker, Popup, useMap, Polyline} from "react-leaflet";
import L from "leaflet";
import { fetchbranches } from '../../services/configService';
import { fetchWaypoints } from '../../services/openStreetMapService';
import LoadingSpinner from '../common/LoadingSpinner';
import Modal from '../common/Modal';
import { formatDistance, formatDuration } from '../../utils/helpers';
import { ConfigContext } from '../../contexts/ConfigContext';
import "leaflet-routing-machine/dist/leaflet-routing-machine.css";
import "leaflet/dist/leaflet.css";
import { FaArrowLeft, FaArrowRight, FaAngleDoubleLeft, FaAngleDoubleRight, FaAngleLeft, FaAngleRight, FaArrowUp, FaCircle, FaSignOutAlt, FaUndo, FaFlagCheckered, FaLocationArrow, FaPlay, FaChevronCircleRight, FaChevronCircleLeft} from 'react-icons/fa';

const maneuverIcons = {
  0: <FaArrowLeft className="turn-icon" />,                 // Turn left
  1: <FaArrowRight className="turn-icon" />,                // Turn right
  2: <FaAngleDoubleLeft className="turn-icon sharp" />,     // Sharp left
  3: <FaAngleDoubleRight className="turn-icon sharp" />,    // Sharp right
  4: <FaAngleLeft className="turn-icon slight" />,          // Slight left
  5: <FaAngleRight className="turn-icon slight" />,         // Slight right
  6: <FaArrowUp className="turn-icon" />,                   // Straight
  7: <FaCircle className="roundabout-icon" />,              // Roundabout
  8: <FaSignOutAlt className="roundabout-exit-icon" />,     // Exit roundabout
  9: <FaUndo className="u-turn-icon" />,                    // U-turn
  10: <FaFlagCheckered className="arrival-icon" />,         // Arrive at destination
  11: <FaLocationArrow className="head-icon" />,            // Head (initial direction)
  12: <FaPlay className="depart-icon" />,                   // Depart (start moving)
  13: <FaChevronCircleRight className="keep-icon" />,       // Keep right
  14: <FaChevronCircleLeft className="keep-icon" />,        // Keep left
};

function Directions({ steps }) {
  return (
    <div className="directions">
      {steps.map((step, index) => (
        <div key={index} className="step">
          <span className="icon">{maneuverIcons[step.type] || <FaArrowRight />}</span>
          <div className="info">
            <div className="instruction">{step.instruction}</div>
            <small>
              {formatDistance(step.distance)} — {formatDuration(step.duration)}
            </small>
          </div>
        </div>
      ))}
    </div>
  );
}

const Branchlocation = () => {
    const config = useContext(ConfigContext);
    const [selectedBranch, setSelectedBranch] = useState(null);
    const [routePositions, setRoutePositions] = useState([]);
    const [distanceMeters, setDistanceMeters] = useState(null);
    const [duration, setDuration] = useState(null);
    const [location, setLocation] = useState(null);
    const [branches, setBranches] = useState([]); 
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [steps, setSteps] = useState([]);
    const navigate = useNavigate();

    const locationIcon = new L.Icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    const branchIcon = new L.Icon({
        iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
    });

    useEffect(() => {
        const loadBranches = async () => {
            setLoading(true);
            try {
                const response = await fetchbranches();
                if (response.data.Status === 'OK') {
                    setBranches(response.data.Result);
                } else {
                    setError(response.data.Message || 'Failed to load branches');
                }
            } catch (err) {
                setError(err.response?.data?.Message || 'An error occurred');
            } finally {
                setLoading(false);
            }
        };
        
        loadBranches();
    }, []);

    const FitBounds = (positions) => {
        const map = useMap();
        useEffect(() => {
            if (!positions) {
                return;
            }
            if (positions.length) {
                const bounds = L.latLngBounds(positions);
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }, [positions, map]);
        return null;
    }

    // When user selects a branch, fetch route from ORS API
    useEffect(() => {
        if (!selectedBranch) {
            setRoutePositions([]);
            return;
        }

        const getRoute = async () => {
            const start = [location.lng, location.lat]; // [lng, lat]
            const end = [selectedBranch.lng, selectedBranch.lat]; // [lng, lat]

            const url = `https://api.openrouteservice.org/v2/directions/driving-car?api_key=${config.ORS_API_KEY}&start=${start[0]},${start[1]}&end=${end[0]},${end[1]}`;

            try {
                setLoading(true);
                const response = await fetchWaypoints(url);
                const data = response.data;

                if (data && data.features?.length > 0) {
                    const coords = data.features[0].geometry.coordinates;
                    const latlngs = coords.map((c) => [c[1], c[0]]);
                    setRoutePositions(latlngs);
                    setDistanceMeters(formatDistance(data.features[0].properties.segments[0].distance));
                    setDuration(formatDuration(data.features[0].properties.segments[0].duration));
                    setSteps(data.features[0].properties.segments[0].steps);
                } else {
                    setError('Failed to load waypoint');
                    setRoutePositions([]);
                }
            } catch (err) {
                console.error(err);
                setError(err.response?.data?.Message || err.message || 'An error occurred');
                setRoutePositions([]);
            } finally {
                setLoading(false);
            }
        };

        getRoute();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedBranch]);

    useEffect(() => {
        if (location) return;

        const getGPSLocation = () => {
            if (!navigator.geolocation) {
                setError("Geolocation is not supported by your browser.");
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setLocation({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                    setError(null);
                },
                 (error) => {
                    console.log(error);
                    /*
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            setError("User denied the request for Geolocation.");
                            break;
                        case error.POSITION_UNAVAILABLE:
                            setError("Location information is unavailable.");
                            break;
                        case error.TIMEOUT:
                            setError("The request to get user location timed out.");
                            break;
                        case error.UNKNOWN_ERROR:
                            setError("An unknown error occurred.");
                            break;
                        default:
                            setError("An unknown error occurred.");
                            break;

                    }*/
                    getLocationByIP();
    }
            );
        };

        const getLocationByIP = async () => {
            try {
                const res = await fetch("https://ipwho.is/");
                const data = await res.json();
                const numLat = Number(data.latitude);
                const numLng = Number(data.longitude);
                setLocation({
                    lat: numLat,
                    lng: numLng
                });
	
            }catch (err) {
                console.error("Error at getLocationByIP:", err);
                setError("Error : " + err.message)
            }
        };

        getGPSLocation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const onSelectBranch = (branch) => {
        setSelectedBranch(branch);
    };

    return (
        <div className="location-container">
            {loading && <LoadingSpinner />}

            <h2>Branches</h2>
            
            <div style={{ display: 'flex', height: '80vh' }}>
                <div style={{ flex: 1 }}>
                    {location ? (
                        <>
                        <MapContainer
                            center={[location.lat, location.lng]}
                            zoom={8}
                            scrollWheelZoom={true}
                            style={{ height: "100%", width: "100%" }}
                        >
                            <TileLayer
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                attribution="© OpenStreetMap contributors"
                            />
                            {/* All branches */}
                            {branches.map((place) => (
                                !isNaN(Number(place.lat)) && !isNaN(Number(place.lng)) && (
                                    <Marker
                                        key={place.branch_code}
                                        position={[Number(place.lat), Number(place.lng)]}
                                        icon={branchIcon}
                                        eventHandlers={{ click: () => onSelectBranch(place) }}
                                    >
                                        <Popup>
                                        {place.branch_name}
                                        {selectedBranch && selectedBranch.branch_code === place.branch_code && (
                                            <>
                                            <br />
                                            <b>Distance: {distanceMeters}</b>
                                            <br />
                                            <b>Duration: {duration}</b>
                                            </>
                                        )}
                                        </Popup>
                                    </Marker>
                                )
                            ))}

                            <Marker position={[location.lat, location.lng]} icon={locationIcon}>
                                <Popup>
                                    <b>You are here</b>
                                </Popup>
                            </Marker>

                            {/* Draw route if exists */}
                            {routePositions.length > 0 && (
                                <>
                                    <Polyline positions={routePositions} color="blue" />
                                    <FitBounds positions={routePositions} />
                                </>
                            )}

                        </MapContainer>
                        </>
                    ) : (
                        <>
                        <LoadingSpinner />
                        </>
                    )}
                </div>

                {/* Directions panel */}
                {selectedBranch && steps.length > 0 && (
                    <div style={{ width: '300px', padding: '10px', overflowY: 'auto', borderLeft: '1px solid #ccc' }}>
                        <h3>Directions to {selectedBranch.branch_name}</h3>
                        <Directions steps={steps} />
                    </div>
                )}
            </div>

            
            <div className="recovery-links align-center">
                <button type="button" onClick={() => navigate('/login')}>
                 Back to Login
                </button>
            </div>

            <Modal
                isOpen={!!error}
                onClose={() => setError(null)}
                title="Error"
                message={error}
            />
        </div>
    );
}

export default Branchlocation;