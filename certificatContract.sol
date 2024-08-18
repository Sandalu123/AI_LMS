// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateSystem {
    struct Certificate {
        string issuerName;
        string receiverName;
        string courseName;
        string department;
        uint256 issuedDate;
        uint256 expiryDate;
        bool isValid;
    }

    mapping(bytes32 => Certificate) public certificates;
    address public owner;

    event CertificateIssued(
        bytes32 indexed certificateId,
        string issuerName,
        string receiverName,
        string courseName,
        string department,
        uint256 issuedDate,
        uint256 expiryDate
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    function issueCertificate(
        string memory _issuerName,
        string memory _receiverName,
        string memory _courseName,
        string memory _department,
        uint256 _expiryDate
    ) public onlyOwner returns (bytes32) {
        bytes32 certificateId = keccak256(abi.encodePacked(_receiverName, _courseName, block.timestamp));
        uint256 issuedDate = block.timestamp;

        certificates[certificateId] = Certificate(
            _issuerName,
            _receiverName,
            _courseName,
            _department,
            issuedDate,
            _expiryDate,
            true
        );

        emit CertificateIssued(
            certificateId,
            _issuerName,
            _receiverName,
            _courseName,
            _department,
            issuedDate,
            _expiryDate
        );

        return certificateId;
    }

    function validateCertificate(bytes32 _certificateId) public view returns (bool, Certificate memory) {
        Certificate memory cert = certificates[_certificateId];
        return (cert.isValid && cert.expiryDate > block.timestamp, cert);
    }

    function revokeCertificate(bytes32 _certificateId) public onlyOwner {
        require(certificates[_certificateId].isValid, "Certificate is not valid or does not exist");
        certificates[_certificateId].isValid = false;
    }
}